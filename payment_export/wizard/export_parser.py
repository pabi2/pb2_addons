# -*- coding: utf-8 -*-
from openerp import api, models, _
from openerp.exceptions import Warning as UserError


class DocumentExportParser(models.TransientModel):
    _inherit = 'document.export.parser'
    _description = 'Export Document'

    @api.multi
    def export_file(self):
        res = super(DocumentExportParser, self).export_file()
        if res:
            self.ensure_one()
            payment_export_id = self.env.context.get('active_id', False)
            payment_export_model = self.env.context.get('active_model', '')
            self.env[payment_export_model].browse(payment_export_id)
        return res

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
            raise UserError(
                _('Not Export Config for %s') % (export.journal_id.name,))
        return res
