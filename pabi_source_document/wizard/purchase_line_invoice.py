# -*- coding: utf-8 -*-
from openerp import api, models


class PurchaseLineInvoice(models.TransientModel):
    _inherit = 'purchase.order.line_invoice'

    @api.model
    def _make_invoice_by_partner(self, partner, orders, lines_ids):
        inv_id = super(PurchaseLineInvoice, self).\
            _make_invoice_by_partner(partner, orders, lines_ids)
        if orders:
            order = orders[0]
            invoice = self.env['account.invoice'].browse(inv_id)
            invoice.write({
                'source_document_id': '%s,%s' % ('purchase.order', order.id),
                'source_document': order.name,
            })
        return inv_id
