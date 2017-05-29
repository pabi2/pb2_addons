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
        # dimensions = Analytic._analytic_dimensions()
        # for d in dimensions:
        #     for r in res:
        #         r[2].update({d: move[d].id})
        # Find analytic id (so that, it can consume budget)
        for r in res:
            analytic_account = Analytic.create_matched_analytic(move)
            if analytic_account:
                r[2]['analytic_account_id'] = analytic_account.id
        return res
