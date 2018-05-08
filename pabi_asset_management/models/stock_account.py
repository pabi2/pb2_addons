# -*- coding: utf-8 -*-
from openerp import models, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _prepare_account_move_line(self, move, qty, cost,
                                   credit_account_id, debit_account_id):
        # Overwrite by asset value in stock.move
        if move.asset_value > 0.0:
            cost = move.asset_value
        res = super(StockQuant, self).\
            _prepare_account_move_line(move, qty, cost,
                                       credit_account_id, debit_account_id)
        asset_profile_id = move.product_id.asset_profile_id.id
        stock_account_id = move.product_id.stock_valuation_account_id.id
        for r in res:
            if r[2]['account_id'] == stock_account_id:
                r[2]['asset_profile_id'] = asset_profile_id
                r[2]['stock_move_id'] = move.id
                r[2]['parent_asset_id'] = \
                    move.purchase_line_id.parent_asset_id.id
        return res
