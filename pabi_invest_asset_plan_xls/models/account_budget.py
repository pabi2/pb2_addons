# -*- coding: utf-8 -*-
from openerp import models, fields


class BudgetPlan(models.Model):
    _inherit = 'invest.asset.plan'

    plan_history_line_ids = fields.One2many(
        'budget.plan.history',
        'invest_asset_plan_id',
        string="Invest Asset Plan History",
    )
    attachment_ids = fields.One2many(
        'ir.attachment',
        'invest_asset_plan_id',
        string='Attachments',
    )
