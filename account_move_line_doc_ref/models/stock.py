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
            picking = move.picking_id
            if picking:
                res[2].update(doc_ref=picking.name,
                              doc_id='%s,%s' % ('stock.picking', picking.id))
        return result
