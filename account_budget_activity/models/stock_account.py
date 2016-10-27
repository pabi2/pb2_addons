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
        AnayticAccount = self.env['account.analytic.account']
        dimensions = AnayticAccount._analytic_dimensions()
        for d in dimensions:
            for r in res:
                r[2].update({d: move[d].id})
        return res
