# -*- coding: utf-8 -*-
from openerp import models, fields


class BudgetPlan(models.Model):
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
