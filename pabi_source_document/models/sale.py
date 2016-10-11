# -*- coding: utf-8 -*-
from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_invoice_create(self, grouped=False,
                              states=None, date_invoice=False):
        invoice_id = super(SaleOrder, self).\
            action_invoice_create(grouped=grouped,
                                  states=states,
                                  date_invoice=date_invoice)
        if invoice_id:
            for order in self:
                invoice = self.env['account.invoice'].browse(invoice_id)
                invoice.write({
                    'source_document_id': '%s,%s' % (self._model, order.id),
                    'source_document': order.name,
                })
        return invoice_id
