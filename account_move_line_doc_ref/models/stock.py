# -*- coding: utf-8 -*-
from openerp import models, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _prepare_account_move_line(self, move, qty, cost,
                                   credit_account_id, debit_account_id):
        result = super(StockQuant, self).\
            _prepare_account_move_line(move, qty, cost,
                                       credit_account_id,
                                       debit_account_id)
        for res in result:
            res[2].update(doc_ref=move.picking_id and
                          move.picking_id.name or False)
        return result
