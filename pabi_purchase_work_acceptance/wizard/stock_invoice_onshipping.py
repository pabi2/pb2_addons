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
