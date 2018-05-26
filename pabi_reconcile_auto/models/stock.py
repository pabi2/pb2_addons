# -*- coding: utf-8 -*-
from openerp import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_done(self):
        res = super(StockMove, self).action_done()
        MoveLine = self.env['account.move.line']
        for move in self:
            picking = move.picking_id
            # Reconcile GR/IR with SO/PO invoices move lines
            pick_mlines = MoveLine.search([('ref', '=', picking.name)])
            # TODO: This doesn't seem to be cost effective yet.
            if pick_mlines:
                sale = picking.sale_id
                purchase = picking.move_lines.\
                    mapped('purchase_line_id').mapped('order_id')
                invoices = sale.mapped('invoice_ids') | \
                    purchase.mapped('invoice_ids')
                inv_mlines = invoices.mapped('move_id.line_id')
                mlines = inv_mlines | pick_mlines
                mlines.reconcile_special_account()
        return res
