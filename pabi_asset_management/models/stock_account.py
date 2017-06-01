# -*- coding: utf-8 -*-
from openerp import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _prepare_account_move_line(self, move, qty, cost,
                                   credit_account_id, debit_account_id):
        res = super(StockQuant, self).\
            _prepare_account_move_line(move, qty, cost,
                                       credit_account_id, debit_account_id)
        # For PABI2 case, we use different approach in determining asset_categ
        # As such, we need to clear it first and reassign again.
        for r in res:
            r[2].update({'asset_category_id': False,
                         'analytic_account_id': False, })
        # If stock valuation account used, it means this is an asset
        asset_category_id = move.product_id.asset_category_id.id
        stock_account_id = move.product_id.stock_valuation_account_id.id
        for r in res:
            if r[2]['account_id'] == stock_account_id:
                r[2]['asset_category_id'] = asset_category_id
                r[2]['stock_move_id'] = move.id
                r[2]['parent_asset_id'] = \
                    move.purchase_line_id.parent_asset_id.id
        # Recalculate analytic
        Analytic = self.env['account.analytic.account']
        for r in res:
            if r[2]['asset_category_id']:
                analytic_account = Analytic.create_matched_analytic(move)
                if analytic_account:
                    r[2]['analytic_account_id'] = analytic_account.id
        return res
