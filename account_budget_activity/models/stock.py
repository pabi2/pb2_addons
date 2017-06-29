# -*- coding: utf-8 -*-
from openerp import api, models
from .account_activity import ActivityCommon


class StockMove(ActivityCommon, models.Model):
    _inherit = 'stock.move'

    @api.model
    def _create_invoice_line_from_vals(self, move, invoice_line_vals):
        AnayticAccount = self.env['account.analytic.account']
        dimensions = AnayticAccount._analytic_dimensions()
        for d in dimensions:
            invoice_line_vals.update({d: move.purchase_line_id[d].id})
        return super(StockMove, self).\
            _create_invoice_line_from_vals(move, invoice_line_vals)
