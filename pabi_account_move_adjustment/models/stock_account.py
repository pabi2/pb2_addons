# -*- coding: utf-8 -*-
from openerp import models, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.v7
    def _create_account_move_line(self, cr, uid, quants, move,
                                  credit_account_id, debit_account_id,
                                  journal_id, context=None):
        # send context stock to account_move
        location_obj = self.pool.get('stock.location')
        location_from = move.location_id
        location_to = quants[0].location_id
        company_from = location_obj._location_owner(cr, uid, location_from, context=context)
        company_to = location_obj._location_owner(cr, uid, location_to, context=context)
        context.update({'stock_move_id': move})
        if company_to and (move.location_id.usage not in ('internal', 'transit') and move.location_dest_id.usage == 'internal' or company_from != company_to):
            if context.get('default_inv_adjust'):
                acc_output = move.product_id.categ_id.\
                    property_stock_account_output_categ.id
                credit_account_id = acc_output
        res = super(StockQuant, self)._create_account_move_line(
                cr, uid, quants, move, credit_account_id, debit_account_id,
                journal_id, context)
        return res
