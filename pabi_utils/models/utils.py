# -*- coding: utf-8 -*-
from openerp import models, api, _


class PABIUtils(models.AbstractModel):
    _name = 'pabi.utils'
    _description = 'Useful Functions'

    @api.model
    def _track_line_change(self, msg_title, fk_field, line, change_dict):
        """ This method is called from line object (i.e., sale.order.line)
            to post message in head object (i..e, sale.order)
        :param msg_title: char, message title in bold.
        :param fk_field: char, foreign key field to header object
        :param line: obj, line object passed in
        :param change_dict: change values, i..e, {'amount': 100, 'unit': 2}
        :return: None
        """
        detail = []
        for f, new_val in change_dict.iteritems():
            field = line._fields[f]
            if new_val:
                old_val = line[f]
                if field.type == 'float':
                    old_val = '{:,.2f}'.format(old_val)
                    new_val = '{:,.2f}'.format(new_val)
                elif field.type == 'integer':
                    old_val = '{:,.0f}'.format(old_val)
                    new_val = '{:,.0f}'.format(new_val)
                elif field.type == 'many2one':
                    old_val = old_val.display_name
                    new_val = new_val.display_name
                elif field.type in ['many2many', 'one2many']:
                    new_ids = new_val[0][2]
                    new_val = old_val.search([('id', 'in', new_ids)])
                    old_val = ','.join([x.display_name for x in old_val])
                    new_val = ','.join([x.display_name for x in new_val])
                detail.append(_('<li><b>%s</b>: %s → %s</li>') %
                              (field.string, old_val, new_val))
        if detail:
            message = '<h3>%s</h3><ul>%s</ul>' % (msg_title, ''.join(detail))
            line[fk_field].message_post(body=message)
