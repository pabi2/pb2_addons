# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountBudget(models.Model):
    _inherit = 'account.budget'

    budgeted_revenue_external = fields.Float(
        string='Total External Revenue',
        compute='_compute_budgeted_overall',
        store=True,
    )
    budgeted_revenue_internal = fields.Float(
        string='Total Internal Revenue',
        compute='_compute_budgeted_overall',
        store=True,
    )
    budgeted_expense_external = fields.Float(
        string='Total External Expense',
        compute='_compute_budgeted_overall',
        store=True,
    )
    budgeted_expense_internal = fields.Float(
        string='Total Internal Expense',
        compute='_compute_budgeted_overall',
        store=True,
    )

    @api.multi
    @api.depends('budget_revenue_line_unit_base',
                 'budget_expense_line_unit_base',
                 'budget_revenue_line_project_base',
                 'budget_expense_line_project_base',
                 'budget_revenue_line_personnel',
                 'budget_expense_line_personnel',
                 'budget_revenue_line_invest_asset',
                 'budget_expense_line_invest_asset',
                 'budget_revenue_line_invest_construction',
                 'budget_expense_line_invest_construction')
    def _compute_budgeted_overall(self):
        super(AccountBudget, self)._compute_budgeted_overall()
        for rec in self:
            revenue_external = 0.0
            revenue_internal = 0.0
            expense_external = 0.0
            expense_internal = 0.0
            for line in rec.budget_revenue_line_ids:
                if line.charge_type == 'external':
                    revenue_external += line.planned_amount
                else:
                    revenue_internal += line.planned_amount
            for line in rec.budget_expense_line_ids:
                if line.charge_type == 'external':
                    expense_external += line.planned_amount
                else:
                    expense_internal += line.planned_amount
            rec.budgeted_revenue_external = revenue_external
            rec.budgeted_revenue_internal = revenue_internal
            rec.budgeted_expense_external = expense_external
            rec.budgeted_expense_internal = expense_internal

    @api.multi
    def _get_future_plan_amount(self):
        """ Overwrite """
        self.ensure_one()
        Period = self.env['account.period']
        period_num = Period.get_num_period_by_period()  # Now
        future_plan = 0.0
        for line in self.budget_expense_line_ids.\
                filtered(lambda l: l.charge_type == 'external'):  # Add this
            for i in range(period_num, 13):
                future_plan += line['m%s' % (i,)]
        return future_plan


class AccountBudgetLine(models.Model):
    _inherit = "account.budget.line"

    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        required=True,
        default='external',
        help="Specify whether the budget plan line is for Internal Charge or "
        "External Charge. Internal charged is for Unit Based only."
    )
