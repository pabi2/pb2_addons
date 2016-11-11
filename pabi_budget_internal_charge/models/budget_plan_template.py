# -*- coding: utf-8 -*-
from openerp import models, fields, api
# from openerp.addons.pabi_chartfield.models.chartfield \
#     import ChartField


class BudgetPlanLineTemplate(models.Model):
    _inherit = "budget.plan.line.template"

    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        required=True,
        default='external',
        help="Specify whether the budget plan line is for Internal Charge or "
        "External Charge. Internal charged is for Unit Based only."
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
        required=True,
        default='expense',
        help="Specify whether the budget plan line is of Revenue or Expense. "
        "Revenue is for Unit Based only."
    )


class BudgetPlanCommon(object):

    # Overwrite
    @api.multi
    @api.depends('plan_line_ids',
                 'plan_revenue_line_ids',
                 'plan_expense_line_ids')
    def _compute_planned_overall(self):
        for rec in self:
            amounts = rec.plan_revenue_line_ids.mapped('planned_amount')
            rec.planned_revenue = sum(amounts)
            amounts = rec.plan_expense_line_ids.mapped('planned_amount')
            rec.planned_expense = sum(amounts)
            rec.planned_overall = rec.planned_revenue - rec.planned_expense
