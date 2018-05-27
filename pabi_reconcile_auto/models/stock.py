# -*- coding: utf-8 -*-
from openerp import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_done(self):
        res = super(StockMove, self).action_done()
        MoveLine = self.env['account.move.line']
        Auto = self.env['account.auto.reconcile']
        # Case GR/IR, use order_number as auto_reconcile_id
        for picking in self.mapped('picking_id'):
            pick_mlines = MoveLine.search([('ref', '=', picking.name)])
            if pick_mlines:
                account_moves = False
                object = False
                # Case picking from SO
                if picking.sale_id:
                    account_moves = pick_mlines.mapped('move_id')
                    object = picking.sale_id
                else:
                    purchase = picking.move_lines.\
                        mapped('purchase_line_id.order_id')
                    if purchase:
                        account_moves = pick_mlines.mapped('move_id')
                        object = purchase
                # Got something to reconcile
                if account_moves and object:
                    auto_id = Auto.get_auto_reconcile_id(object)
                    account_moves.write({'auto_reconcile_id': auto_id})
                    mlines = MoveLine.search([('auto_reconcile_id',
                                               '=', auto_id)])
                    mlines.reconcile_special_account()
        return res
