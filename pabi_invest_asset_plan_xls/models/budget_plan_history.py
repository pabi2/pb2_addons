# -*- coding: utf-8 -*-
from openerp import models, fields


class BudgetPlanHistory(models.Model):
    _inherit = 'budget.plan.history'

    invest_asset_plan_id = fields.Many2one(
        'invest.asset.plan',
        string="Invest Asset Plan",
        readonly=False,
    )
