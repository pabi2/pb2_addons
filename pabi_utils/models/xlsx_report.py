# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class XLSXReport(models.AbstractModel):
    """ Common class for xlsx reporting wizard """
    _name = 'xlsx.report'

    name = fields.Char(
        string='File Name',
        readonly=True,
    )
    data = fields.Binary(
        string='File',
        readonly=True,
    )
    state = fields.Selection(
        [('choose', 'choose'),
         ('get', 'get')],
        default='choose',
    )

    @api.multi
    def action_get_report(self):
        self.ensure_one()
        Export = self.env['export.xlsx.template']
        Attachment = self.env['ir.attachment']
        template = Attachment.search([('res_model', '=', self._name)])
        if len(template) != 1:
            raise ValidationError(
                _('The report template "%s" must be single') % self._name)
        out_file, out_name = Export._export_template(template,
                                                     self._name, self.id)
        self.write({'state': 'get', 'data': out_file, 'name': out_name})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
