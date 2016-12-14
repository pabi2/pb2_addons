# -*- coding: utf-8 -*-
from openerp import models, fields


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


# class BudgetPlanCommon(object):
#
#         @api.multi
#         @api.depends('plan_line_ids',
#                      'plan_revenue_line_ids',
#                      'plan_expense_line_ids')
#         def _compute_planned_overall(self):
#             for rec in self:
#                 revenue_external = 0.0
#                 revenue_internal = 0.0
#                 expense_external = 0.0
#                 expense_internal = 0.0
#                 for line in rec.plan_revenue_line_ids:
#                     if line.charge_type == 'external':
#                         revenue_external += line.planned_amount
#                     else:
#                         revenue_internal += line.planned_amount
#                 for line in rec.plan_external_line_ids:
#                     if line.charge_type == 'external':
#                         expense_external += line.planned_amount
#                     else:
#                         expense_internal += line.planned_amount
#                 rec.planned_revenue_external = revenue_external
#                 rec.planned_revenue_internal = revenue_internal
#                 rec.planned_expense_external = expense_external
#                 rec.planned_expense_internal = expense_internal
#                 rec.planned_revenue = revenue_external + revenue_internal
#                 rec.planned_expense = expense_external + expense_internal
#                 rec.planned_overall = rec.planned_revenue - rec.planned_expense
