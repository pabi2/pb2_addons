# -*- coding: utf-8 -*-

from openerp import models, api


class StockInvoiceOnShipping(models.TransientModel):
    _inherit = 'stock.invoice.onshipping'

    @api.model
    def default_get(self, fields):
        res = super(StockInvoiceOnShipping,
                    self).default_get(fields)
        Picking = self.env['stock.picking']
        picking_ids = self.env.context['active_ids'] or []
        picking = Picking.browse(picking_ids)
        res['invoice_date'] = picking.acceptance_id.date_invoice
        return res

    @api.multi
    def create_invoice(self):
        invoice_ids = super(StockInvoiceOnShipping, self).create_invoice()
        active_id = self._context.get('active_id')
        picking = self.env['stock.picking'].browse(active_id)
        picking.ref_invoice_ids = invoice_ids
        return invoice_ids
