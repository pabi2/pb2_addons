# -*- coding: utf-8 -*-
from openerp import models, fields, api


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    no_journal_entry = fields.Boolean(
        string='No Journal Entry',
    )


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _create_account_move_line(self, quants, move, credit_account_id,
                                  debit_account_id, journal_id):
        if move.inventory_id.no_journal_entry:
            return True
        super(StockQuant, self)._create_account_move_line(
            quants, move, credit_account_id, debit_account_id, journal_id)
