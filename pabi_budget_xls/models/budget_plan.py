# -*- coding: utf-8 -*-
from openerp import models, fields


class BudgetPlanUnit(models.Model):
    _inherit = 'budget.plan.unit'

    plan_history_line_ids = fields.One2many(
        'budget.plan.history',
        'plan_id',
        string="Budget Plan History",
    )
    attachment_ids = fields.One2many(
        'ir.attachment',
        'budget_plan_id',
        string='Attachments',
    )


class InvestAssetPlan(models.Model):
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
