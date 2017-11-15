# -*- coding: utf-8 -*-
from openerp import api, models
from .account_activity import ActivityCommon


class ProcurementOrder(ActivityCommon, models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _run_move_create(self, procurement):
        res = super(ProcurementOrder, self)._run_move_create(procurement)
        AnayticAccount = self.env['account.analytic.account']
        dimensions = AnayticAccount._analytic_dimensions()
        for d in dimensions:
            res.update({d: procurement[d].id})
        # We need to add sale_line_id to stock_move, for budget_transition
        res['sale_line_id'] = procurement.sale_line_id.id
        # --
        return res
