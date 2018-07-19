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
    control_ext_charge_only = fields.Boolean(
        string='Split Internal/External',
        related='fiscalyear_id.control_ext_charge_only',
    )
    past_consumed_internal = fields.Float(
        string='Past Actuals',
        compute='_compute_past_future_rolling_internal',
        help="Actual for the past months (internal)",
    )
    future_plan_internal = fields.Float(
        string='Future Plan',
        compute='_compute_past_future_rolling_internal',
        help="Future plan amount, including this month (internal)",
    )
    rolling_internal = fields.Float(
        string='Rolling',
        compute='_compute_past_future_rolling_internal',
        help="Past Actual + Future Plan (internal)",
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
        """ Overwrite """
        for rec in self:
            revenue_external = 0.0
            revenue_internal = 0.0
            expense_external = 0.0
            expense_internal = 0.0
            revenue_lines = rec.budget_revenue_line_unit_base or \
                rec.budget_revenue_line_project_base or \
                rec.budget_revenue_line_personnel or \
                rec.budget_revenue_line_invest_asset or \
                rec.budget_revenue_line_invest_construction
            expense_lines = rec.budget_expense_line_unit_base or \
                rec.budget_expense_line_project_base or \
                rec.budget_expense_line_personnel or \
                rec.budget_expense_line_invest_asset or \
                rec.budget_expense_line_invest_construction
            for line in revenue_lines:
                if line.charge_type == 'external':
                    revenue_external += line.planned_amount
                else:
                    revenue_internal += line.planned_amount
            for line in expense_lines:
                if line.charge_type == 'external':
                    expense_external += line.planned_amount
                else:
                    expense_internal += line.planned_amount
            rec.budgeted_revenue_external = revenue_external
            rec.budgeted_revenue_internal = revenue_internal
            rec.budgeted_expense_external = expense_external
            rec.budgeted_expense_internal = expense_internal
            rec.budgeted_revenue = revenue_external + revenue_internal
            rec.budgeted_expense = expense_external + expense_internal

    @api.multi
    def _budget_expense_lines_hook(self):
        self.ensure_one()
        if self.fiscalyear_id.control_ext_charge_only:
            return self.budget_expense_line_ids.\
                filtered(lambda l: l.charge_type == 'external')
        else:
            return self.budget_expense_line_ids

    @api.multi
    def _get_past_consumed_domain(self):
        self.ensure_one()
        dom = super(AccountBudget, self)._get_past_consumed_domain()
        if self.fiscalyear_id.control_ext_charge_only:
            dom += [('charge_type', '=', 'external')]
        return dom

    @api.model
    def _get_budget_monitor(self, fiscal, budget_type,
                            budget_level, resource,
                            blevel=False):
        """ If set to control only external charge """
        monitors = super(AccountBudget, self).\
            _get_budget_monitor(fiscal, budget_type,
                                budget_level, resource,
                                blevel=blevel)
        if blevel and fiscal.control_ext_charge_only:
            monitors = monitors.filtered(lambda l: l.charge_type == 'external')
        return monitors

    @api.multi
    def _get_past_actual_amount_internal(self):
        self.ensure_one()
        Consume = self.env['budget.consume.report']
        # Period = self.env['account.period']
        # current_period = Period.find()
        dom = [('fiscalyear_id', '=', self.fiscalyear_id.id),
               ('budget_method', '=', 'expense'),
               ('charge_type', '=', 'internal'),
               # May said, past actual should include the future one
               # ('period_id', '<=', current_period.id),
               ]
        consumes = Consume.search(dom)
        return sum(consumes.mapped('amount_actual'))

    @api.multi
    def _get_future_plan_amount_internal(self):
        self.ensure_one()
        Period = self.env['account.period']
        period_num = 0
        this_period_date_start = Period.find().date_start

        if self.fiscalyear_id.date_start > this_period_date_start:
            period_num = 0
        elif self.fiscalyear_id.date_stop < this_period_date_start:
            period_num = 12
        else:
            period_num = Period.get_num_period_by_period()
        future_plan = 0.0
        expense_lines = self.budget_expense_line_ids.\
            filtered(lambda l: l.charge_type == 'internal')
        for line in expense_lines:
            for i in range(period_num + 1, 13):
                future_plan += line['m%s' % (i,)]
        return future_plan

    @api.multi
    def _compute_past_future_rolling_internal(self):
        """ For internal charge """
        for budget in self:
            if not budget.fiscalyear_id.control_ext_charge_only:
                continue
            budget.past_consumed_internal = \
                budget._get_past_actual_amount_internal()
            budget.future_plan_internal = \
                budget._get_future_plan_amount_internal()
            budget.rolling_internal = \
                budget.past_consumed_internal + budget.future_plan_internal


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
    income_section_id = fields.Many2one(
        'res.section',
        string='Income Section',
        domain=[('internal_charge', '=', True)],
    )
