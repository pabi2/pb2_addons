# -*- coding: utf-8 -*-
from openerp import models, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.v7
    def _create_account_move_line(self, cr, uid, quants, move,
                                  credit_account_id, debit_account_id,
                                  journal_id, context=None):
        # send context stock to account_move
        context.update({'stock_move_id': move})
        res = super(StockQuant, self)._create_account_move_line(
                cr, uid, quants, move, credit_account_id, debit_account_id,
                journal_id, context)
        return res
