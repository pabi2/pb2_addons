# -*- coding: utf-8 -*-
from openerp import api, models, _
from openerp.exceptions import ValidationError


class DocumentExportParser(models.TransientModel):
    _inherit = 'document.export.parser'
    _description = 'Export Document'

    @api.multi
    def export_file(self):
        self.ensure_one()
        attachment_id = super(DocumentExportParser, self).export_file()
        payment_export_id = self.env.context.get('active_id', False)
        model = self.env.context.get('active_model', '')
        payment_export = self.env[model].browse(payment_export_id)
        # Check case payment export
        if model in ['payment.export']:
            payment_export._check_payment_export_line()
        payment_export.write({'exported': True,
                              'state': 'done'})
        return attachment_id

    @api.model
    def default_get(self, fields):
        res = super(DocumentExportParser, self).default_get(fields)
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        export = self.env[active_model].browse(active_id)
        configs = self.env['journal.export.config'].search(
            [('journal_id', '=', export.journal_id.id),
             ('transfer_type', '=', export.transfer_type)])
        if configs:
            res['config_id'] = configs[0].config_id.id
        else:
            raise ValidationError(
                _('Not Export Config for %s') % (export.journal_id.name,))
        return res
