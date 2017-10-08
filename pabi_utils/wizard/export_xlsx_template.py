# -*- coding: utf-8 -*-
import os
import openpyxl
import base64
import cStringIO
import re
from datetime import datetime, timedelta
from ast import literal_eval

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


def get_line_max(line_field):
    """ i.e., line_field = line_ids[100], mas = 100 else 0 """
    if '[' in line_field and ']' in line_field:
        i = line_field.index('[')
        j = line_field.index(']')
        max_str = line_field[i + 1:j]
        try:
            if len(max_str) > 0:
                return (line_field[:i], int(max_str))
            else:
                return (line_field, False)
        except:
            return (line_field, False)


def split_row_col(pos):
    match = re.match(r"([a-z]+)([0-9]+)", pos, re.I)
    if not match:
        raise ValidationError(_('Position %s is not valid') % (pos, ))
    col, row = match.groups()
    return col, int(row)


def get_sheet_by_name(book, name):
    """ Get sheet by name for openpyxl """
    i = 0
    for sheetname in book.sheetnames:
        if sheetname == name:
            return book.worksheets[i]
        i += 1
    raise ValidationError(_("'%s' sheet not found") % (name,))


class ExportXlsxTemplate(models.TransientModel):
    """ This wizard is used with the template (ir.attachment) to export
    xlsx template filled with data form the active record """
    _name = 'export.xlsx.template'

    name = fields.Char(
        string='File Name',
        readonly=True,
    )
    data = fields.Binary(
        string='File',
        readonly=True,
    )
    template_id = fields.Many2one(
        'ir.attachment',
        string='Template',
        required=True,
        ondelete='set null',
        domain="[('res_model', '=', res_model)]",
    )
    res_id = fields.Integer(
        string='Resource ID',
        readonly=True,
        required=True,
    )
    res_model = fields.Char(
        string='Resource Model',
        readonly=True,
        required=True,
    )
    state = fields.Selection(
        [('choose', 'choose'),
         ('get', 'get')],
        default='choose',
    )

    @api.model
    def default_get(self, fields):
        res_model = self._context.get('active_model', False)
        res_id = self._context.get('active_id', False)
        template = self.env['ir.attachment'].\
            search([('res_model', '=', res_model)])
        if not template:
            raise ValidationError(_('No template found!'))
        defaults = super(ExportXlsxTemplate, self).default_get(fields)
        if not template.datas:
            raise ValidationError(_('No file in %s') % (template.name,))
        defaults['template_id'] = len(template) == 1 and template.id or False
        defaults['res_id'] = res_id
        defaults['res_model'] = res_model
        return defaults

    @api.model
    def _get_val(self, record, field):
        for f in field.split('.'):
            record = record[f]
        return record

    @api.model
    def _get_line_vals(self, record, line_field, fields):
        """ Get values of this field from record set """
        line_field, max_row = get_line_max(line_field)
        lines = record[line_field]
        if max_row > 0 and len(lines) > max_row:
            raise Exception(
                _('Records in %s exceed max record allowed!') % line_field)
        vals = dict([(field, []) for field in fields])
        for line in lines:
            for field in fields:
                line_copy = line
                for f in field.split('.'):
                    line_copy = line_copy[f]
                vals[field].append(line_copy)
        return (line_field, vals)

    @api.model
    def _fill_workbook_data(self, workbook, record, data_dict):
        """ Fill data from record with format in data_dict to workbook """
        if not record or not data_dict:
            return
        try:
            for sheet_name in data_dict:
                st = get_sheet_by_name(workbook, sheet_name)
                worksheet = data_dict[sheet_name]
                # HEAD
                for rc, field in worksheet.get('_HEAD_', {}).iteritems():
                    st[rc] = self._get_val(record, field)
                # Line Items
                line_fields = filter(lambda l: l != '_HEAD_', worksheet)
                for line_field in line_fields:
                    fields = [field for rc, field
                              in worksheet.get(line_field, {}).iteritems()]
                    line_field, vals = self._get_line_vals(record,
                                                           line_field, fields)
                    for rc, field in worksheet.get(line_field, {}).iteritems():
                        col, row = split_row_col(rc)  # starting point
                        i = 0
                        for val in vals[field]:
                            new_row = row + i
                            new_rc = '%s%s' % (col, new_row)
                            st[new_rc] = val
                            i += 1
        except ValueError, e:
            message = str(e).format(rc)
            raise ValidationError(message)
        except KeyError, e:
            raise ValidationError(_('Key Error: %s') % e)
        except Exception, e:
            raise ValidationError(
                _('Error filling data into excel sheets!\n%s') % e)

    @api.model
    def _export_template(self, template, res_model, res_id):
        data_dict = literal_eval(template.description.strip())
        export_dict = data_dict.get('__EXPORT__', False)
        out_name = template.name
        if not export_dict:  # If there is not __EXPORT__ formula, just export
            out_name = template.datas_fname
            out_file = template.datas
            return (out_file, out_name)
        # Prepare temp file (from now, only xlsx file works for openpyxl)
        decoded_data = base64.decodestring(template.datas)
        ConfParam = self.env['ir.config_parameter']
        ptemp = ConfParam.get_param('path_temp_file') or '/temp'
        stamp = datetime.utcnow().strftime('%H%M%S%f')[:-3]
        ftemp = '%s/temp%s.xlsx' % (ptemp, stamp)
        f = open(ftemp, 'w')
        f.write(decoded_data)
        f.seek(0)
        f.close()
        # Workbook created, temp fie removed
        wb = openpyxl.load_workbook(ftemp)
        os.remove(ftemp)
        # ============= Start working with workbook =============
        record = res_model and self.env[res_model].browse(res_id) or False
        self._fill_workbook_data(wb, record, export_dict)
        # =======================================================
        # Return file as .xlsx
        content = cStringIO.StringIO()
        wb.save(content)
        content.seek(0)  # Set index to 0, and start reading
        out_file = base64.encodestring(content.read())
        if record and 'name' in record and record.name:
            out_name = record.name.replace('/', '')
        return (out_file, '%s.xlsx' % out_name)

    @api.multi
    def act_getfile(self):
        self.ensure_one()
        out_file, out_name = self._export_template(self.template_id,
                                                   self.res_model, self.res_id)
        self.write({'state': 'get', 'data': out_file, 'name': out_name})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'export.xlsx.template',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
