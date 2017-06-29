# -*- coding: utf-8 -*-
from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _action_invoice_create_hook(self, invoice_ids):
        super(SaleOrder, self)._action_invoice_create_hook(invoice_ids)
        invoices = self.env['account.invoice'].browse(invoice_ids)
        invoices.write({
            'source_document_id': '%s,%s' % (self._model, self.id),
            'source_document': self.name,
        })
        return

    # As invoice plan is installed, do it in the HOOK is more efficient.
    # @api.multi
    # def action_invoice_create(self, grouped=False,
    #                           states=None, date_invoice=False):
    #     invoice_id = super(SaleOrder, self).\
    #         action_invoice_create(grouped=grouped,
    #                               states=states,
    #                               date_invoice=date_invoice)
    #     if invoice_id:
    #         for order in self:
    #             invoice = self.env['account.invoice'].browse(invoice_id)
    #             invoice.write({
    #                 'source_document_id': '%s,%s' % (self._model, order.id),
    #                 'source_document': order.name,
    #             })
    #     return invoice_id
