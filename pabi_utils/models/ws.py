# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class PABIUtilsWS(models.AbstractModel):
    _name = 'pabi.utils.ws'
    _description = 'Webservice helper'

    @api.model
    def create_data(self, model, data_dict):
        """ Accept friendly data_dict in following format to create new rec
        Note: this method is deprecated, use friendly_create_data() instead
            {'field1': value1,
             'line_ids': [{
                'field2': value2,
             }]}
        """
        res = {}
        # Final Preparation of fields and data
        fields, data = self._finalize_data_to_load(data_dict)
        load_res = self.env[model].load(fields, data)
        res_id = load_res['ids'] and load_res['ids'][0] or False
        if not res_id:
            res = {
                'is_success': False,
                'result': False,
                'messages': [m['message'] for m in load_res['messages']],
            }
        else:
            res = {
                'is_success': True,
                'result': {
                    'id': res_id,
                },
                'messages': _('Record created successfully'),
            }
        return res

    @api.model
    def friendly_update_data(self, model, data_dict, key_field):
        """ Accept friendly data_dict in following format to update existing rec
        This method, will always delete o2m lines and recreate it.
            data_dict:
            {'field1': value1,
             'line_ids': [{
                'field2': value2,
             }]
            }
            key_field: search field, i.e., number
        """
        res = {}
        # Prepare Header Dict (non o2m)
        if not key_field or key_field not in data_dict:
            raise ValidationError(
                _('Method update_data() key_field is not valid!'))
        rec = self.env[model].search([(key_field, '=', data_dict[key_field])])
        if not rec:
            raise ValidationError(_('Search key "%s" not found!') %
                                  data_dict[key_field])
        elif len(rec) > 1:
            raise ValidationError(_('Search key "%s" found mutiple matches!') %
                                  data_dict[key_field])
        rec_fields = []
        line_fields = []
        for field, model_field in rec._fields.iteritems():
            if field in data_dict and model_field.type != 'one2many':
                rec_fields.append(field)
            elif field in data_dict:
                line_fields.append(field)
        rec_dict = {k: v for k, v in data_dict.iteritems() if k in rec_fields}
        rec_dict = self._finalize_data_to_write(rec, rec_dict)
        # Prepare Line Dict (o2m)
        for line_field in line_fields:
            lines = rec[line_field]
            # First, delete all lines o2m
            lines.unlink()
            final_line_dict = []
            # Loop all o2m lines, and recreate it
            for line_data_dict in data_dict[line_field]:
                rec_fields = []
                line_fields = []
                for field, model_field in rec[line_field]._fields.iteritems():
                    if field in line_data_dict and \
                            model_field.type != 'one2many':
                        rec_fields.append(field)
                    elif field in line_data_dict:
                        line_fields.append(field)
                line_dict = {k: v for k, v in line_data_dict.iteritems()
                             if k in rec_fields}
                if line_fields:
                    raise ValidationError(_('friendly_update_data() support '
                                            'only 1 level of one2many lines'))
                line_dict = self._finalize_data_to_write(lines, line_dict)
                final_line_dict.append((0, 0, line_dict))
            rec_dict[line_field] = final_line_dict
        rec.write(rec_dict)
        res = {
            'is_success': True,
            'result': {
                'id': rec.id,
            },
            'messages': _('Record created successfully'),
        }
        return res

    @api.model
    def friendly_create_data(self, model, data_dict):
        """ Accept friendly data_dict in following format to create data
            data_dict:
            {'field1': value1,
             'field2_id': value2,  # can be ID or name search string
             'line_ids': [{
                'field2': value2,
             }]
            }
        """
        res = {}
        rec = self.env[model].new()  # Dummy reccord
        rec_fields = []
        line_fields = []
        for field, model_field in rec._fields.iteritems():
            if field in data_dict and model_field.type != 'one2many':
                rec_fields.append(field)
            elif field in data_dict:
                line_fields.append(field)
        rec_dict = {k: v for k, v in data_dict.iteritems() if k in rec_fields}
        rec_dict = self._finalize_data_to_write(rec, rec_dict)
        # Prepare Line Dict (o2m)
        for line_field in line_fields:
            final_line_dict = []
            # Loop all o2m lines, and recreate it
            for line_data_dict in data_dict[line_field]:
                rec_fields = []
                line_fields = []
                for field, model_field in rec[line_field]._fields.iteritems():
                    if field in line_data_dict and \
                            model_field.type != 'one2many':
                        rec_fields.append(field)
                    elif field in line_data_dict:
                        line_fields.append(field)
                line_dict = {k: v for k, v in line_data_dict.iteritems()
                             if k in rec_fields}
                if line_fields:
                    raise ValidationError(_('friendly_create_data() support '
                                            'only 1 level of one2many lines'))
                line_dict = self._finalize_data_to_write(rec[line_field],
                                                         line_dict)
                final_line_dict.append((0, 0, line_dict))
            rec_dict[line_field] = final_line_dict
        obj = rec.create(rec_dict)
        res = {
            'is_success': True,
            'result': {
                'id': obj.id,
            },
            'messages': _('Record created successfully'),
        }
        return res

    @api.model
    def _finalize_data_to_write(self, rec, rec_dict):
        """ For many2one, use name search to get id """
        final_dict = {}
        for key, value in rec_dict.iteritems():
            if key in rec_dict.keys() and rec._fields[key].type == 'many2one':
                model = rec._fields[key].comodel_name
                if rec_dict[key] and isinstance(rec_dict[key], basestring):
                    values = self.env[model].name_search(rec_dict[key],
                                                         operator='=')
                    if len(values) > 1:
                        raise ValidationError(
                            _('%s matched more than 1 record') % rec_dict[key])
                    elif not values:
                        raise ValidationError(
                            _('%s found no match.') % rec_dict[key])
                    value = values[0][0]
            final_dict.update({key: value})
        return final_dict

    @api.model
    def _finalize_data_to_load(self, data_dict):
        """
        This method will convert user friendly data_dict
        to load() compatible fields/data
        Currently it is working with multiple line table but with 1 level only
        data_dict = {
            'name': 'ABC',
            'line_ids': ({'desc': 'DESC'},),
            'line2_ids': ({'desc': 'DESC'},),
        }
        to
        fields = ['name', 'line_ids/desc', 'line2_ids/desc']
        data = [('ABC', 'DESC', 'DESC')]
        """
        fields = data_dict.keys()
        data = data_dict.values()
        line_count = 1
        _table_fields = []  # Tuple fields
        for key in fields:
            if isinstance(data_dict[key], list) or \
                    isinstance(data_dict[key], tuple):
                _table_fields.append(key)
        data_array = {}
        for table in _table_fields:
            data_array[table] = False
            data_array[table + '_fields'] = False
            if table in fields:
                i = fields.index(table)
                data_array[table] = data[i] or ()  # ({'x': 1, 'y': 2}, {})
                del fields[i]
                del data[i]
                line_count = max(line_count, len(data_array[table]))
            if data_array[table]:
                data_array[table + '_fields'] = \
                    [table + '/' + key for key in data_array[table][0].keys()]
            fields += data_array[table + '_fields'] or []
        # Data
        datas = []
        for i in range(0, line_count, 1):
            record = []
            for table in _table_fields:
                data_array[table + '_data'] = False
                if data_array[table + '_fields']:
                    data_array[table + '_data'] = \
                        (len(data_array[table]) > i and data_array[table][i] or
                         {key: False for key in data_array[table + '_fields']})
                record += data_array[table + '_data'] and \
                    data_array[table + '_data'].values() or []
            if i == 0:
                datas += [tuple(data + record)]
            else:
                datas += [tuple([False for _x in data] + record)]
        return fields, datas
