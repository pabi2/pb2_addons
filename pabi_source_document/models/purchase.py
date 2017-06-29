# -*- coding: utf-8 -*-
from openerp import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _action_invoice_create_hook(self, invoice_ids):
        super(PurchaseOrder, self)._action_invoice_create_hook(invoice_ids)
        invoices = self.env['account.invoice'].browse(invoice_ids)
        invoices.write({
            'source_document_id': '%s,%s' % (self._model, self.id),
            'source_document': self.name,
        })
        return

# As invoice plan is installed, do it in the HOOK is more efficient.
# @api.multi
# def action_invoice_create(self):
#     invoice_id = super(PurchaseOrder, self).action_invoice_create()
#     if invoice_id:
#         for purchase in self:
#             invoice = self.env['account.invoice'].browse(invoice_id)
#             invoice.write({
#                 'source_document_id': '%s,%s' % (self._model, purchase.id),
#                 'source_document': purchase.name,
#             })
#     return invoice_id
