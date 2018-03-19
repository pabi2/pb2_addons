# -*- coding: utf-8 -*-
from openerp import models, fields, api


class BudgetPlanUnit(models.Model):
    _inherit = "budget.plan.unit"

    planned_revenue_external = fields.Float(
        string='Total External Revenue',
        compute='_compute_planned_overall',
        store=True,
    )
    planned_revenue_internal = fields.Float(
        string='Total Internal Revenue',
        compute='_compute_planned_overall',
        store=True,
    )
    planned_expense_external = fields.Float(
        string='Total External Expense',
        compute='_compute_planned_overall',
        store=True,
    )
    planned_expense_internal = fields.Float(
        string='Total Internal Expense',
        compute='_compute_planned_overall',
        store=True,
    )
    planned_internal_overall = fields.Float(
        string='Total Internal Planned',
        compute='_compute_planned_overall',
        store=True,
    )
    planned_external_overall = fields.Float(
        string='Total External Planned',
        compute='_compute_planned_overall',
        store=True,
    )

    @api.multi
    @api.depends('plan_line_ids',
                 'plan_revenue_line_ids',
                 'plan_expense_line_ids')
    def _compute_planned_overall(self):
        super(BudgetPlanUnit, self)._compute_planned_overall()
        for rec in self:
            revenue_external = 0.0
            revenue_internal = 0.0
            expense_external = 0.0
            expense_internal = 0.0
            for line in rec.plan_revenue_line_ids:
                if line.charge_type == 'external':
                    revenue_external += line.planned_amount
                else:
                    revenue_internal += line.planned_amount
            for line in rec.plan_expense_line_ids:
                if line.charge_type == 'external':
                    expense_external += line.planned_amount
                else:
                    expense_internal += line.planned_amount
            rec.planned_revenue_external = revenue_external
            rec.planned_revenue_internal = revenue_internal
            rec.planned_expense_external = expense_external
            rec.planned_expense_internal = expense_internal
            rec.planned_internal_overall = revenue_internal - expense_internal
            rec.planned_external_overall = revenue_external - expense_external


class BudgetPlanUnitLine(models.Model):
    _inherit = "budget.plan.unit.line"

    income_section_id = fields.Many2one(
        'res.section',
        string='Income Section',
        domain=[('internal_charge', '=', True)],
    )
    income_section_name = fields.Char(
        related='income_section_id.name',
        string='Income Section Name',
        store=True,
        readonly=True,
    )
    income_section_name_short = fields.Char(
        related='income_section_id.name_short',
        string='Income Section Alias',
        store=True,
        readonly=True,
    )
    income_section_code = fields.Char(
        related='income_section_id.code',
        string='Income Section Code',
        store=True,
        readonly=True,
    )

# class BudgetPlanUnitCostControlLine(models.Model):
#     _inherit = 'budget.plan.unit.cost.control.line'
#
#     charge_type = fields.Selection(
#         [('internal', 'Internal'),
#          ('external', 'External')],
#         string='Charge Type',
#         required=True,
#         default='external',
#       help="Specify whether the budget plan line is for Internal Charge or "
#         "External Charge. Internal charged is for Unit Based only."
#     )
