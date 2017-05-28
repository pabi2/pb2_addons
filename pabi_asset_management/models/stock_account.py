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
        Account = self.env['account.account']
        debit_acct = Account.browse(debit_account_id)
        credit_acct = Account.browse(credit_account_id)
        debit_line = res[0][2]
        credit_line = res[1][2]
        # If stock valuation account used, it means this is an asset
        asset_category_id = move.product_id.asset_category_id.id
        if move.product_id.stock_valuation_account_id == debit_acct:
            debit_line['asset_category_id'] = asset_category_id
            debit_line['stock_move_id'] = move.id
        if move.product_id.stock_valuation_account_id == credit_acct:
            credit_line['asset_category_id'] = asset_category_id
            credit_line['stock_move_id'] = move.id
        return [(0, 0, debit_line), (0, 0, credit_line)]
