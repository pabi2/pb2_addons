# -*- coding: utf-8 -*-
from openerp import models, api, fields


class UpdateWAInvoice(models.TransientModel):
    _name = 'update.wa.invoice'

    wa_id = fields.Many2one(
        comodel_name="purchase.work.acceptance",
        string="WA Reference",
        domain=lambda self: self._domain_wa_id(),
        required=True
    )

    @api.multi
    def _domain_wa_id(self):
        wa = self.env['purchase.work.acceptance']
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        dom = []
        if active_model:
            records = self.env[active_model].browse(active_ids)
            work_acceptance = wa.search([
                ('order_id', 'in', records.mapped('source_document_id').ids)])
            dom = \
                [('id', 'in', work_acceptance.ids), ('state', '!=', 'cancel')]
        return dom

    @api.multi
    def action_upd_wa(self):
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        if active_model:
            records = self.env[active_model].browse(active_ids)
            records.write({
                'wa_id': self.wa_id.id, 'wa_origin_id': self.wa_id.id
            })
