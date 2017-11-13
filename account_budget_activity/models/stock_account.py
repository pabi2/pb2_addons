# -*- coding: utf-8 -*-
from openerp import api, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _prepare_account_move_line(self, move, qty, cost,
                                   credit_account_id, debit_account_id):
        res = super(StockQuant, self).\
            _prepare_account_move_line(move, qty, cost,
                                       credit_account_id, debit_account_id)
        Analytic = self.env['account.analytic.account']
        # Profit & Loss account of this product
        bs_accounts = [
            move.product_id.property_stock_account_input.id,
            move.product_id.property_stock_account_output.id,
            move.product_id.categ_id.property_stock_account_input_categ.id,
            move.product_id.categ_id.property_stock_account_output_categ.id,
        ]
        for r in res:
            # For non B&L, we assign analytic
            if r[2]['account_id'] not in bs_accounts:
                analytic_account = Analytic.create_matched_analytic(move)
                if analytic_account:
                    r[2]['analytic_account_id'] = analytic_account.id
        return res
