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
        BudgetLine = self.env['account.budget.line']
        if self.fiscalyear_id.control_ext_charge_only:
            expense_lines = BudgetLine.search([
                ('id', 'in', self.budget_expense_line_ids.ids),
                ('charge_type', '=', 'external')])
            return expense_lines
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
                            blevel=False, extra_dom=[]):
        """ If set to control only external charge """
        if blevel and fiscal.control_ext_charge_only:
            extra_dom = [('charge_type', '=', 'external')]
        monitors = super(AccountBudget, self).\
            _get_budget_monitor(fiscal, budget_type,
                                budget_level, resource,
                                blevel=blevel, extra_dom=extra_dom)
        return monitors

    @api.multi
    def _get_past_actual_amount_internal(self):
        self.ensure_one()
        budget_type_dict = {
            'unit_base': 'section_id',
            'project_base': 'program_id',
            'personnel': False,
            'invest_asset': 'org_id',
            'invest_construction': 'org_id'}
        dimension = budget_type_dict.get(self.chart_view, False)
        # Period = self.env['account.period']
        # current_period = Period.find()
        dom = [('fiscalyear_id', '=', self.fiscalyear_id.id),
               ('budget_method', '=', 'expense'),
               ('charge_type', '=', 'internal'),
               ('chart_view', '=', self.chart_view), ]
        if dimension:
            dom.append((dimension, '=', self[dimension].id))
        sql = """
            select coalesce(sum(amount_actual), 0.0) amount_actual
            from budget_consume_report where %s
        """ % self._domain_to_where_str(dom)
        self._cr.execute(sql)
        amount = self._cr.fetchone()[0]
        return amount

    @api.multi
    def _get_future_plan_amount_internal(self):
        if not self:
            return 0.0
        Period = self.env['account.period']
        Fiscal = self.env['account.fiscalyear']
        BudgetLine = self.env['account.budget.line']
        period_num = 0
        this_period_date_start = Period.find().date_start
        future_plan = 0.0
        self._cr.execute("""
            select distinct fiscalyear_id from account_budget
            where id in %s
        """, (tuple(self.ids), ))
        fiscal_ids = [x[0] for x in self._cr.fetchall()]
        fiscals = Fiscal.browse(fiscal_ids)
        for fiscal in fiscals:
            if fiscal.date_start > this_period_date_start:
                period_num = 0
            elif fiscal.date_stop < this_period_date_start:
                period_num = 12
            else:
                period_num = Period.get_num_period_by_period()
            budgets = self.search([('id', 'in', self.ids),
                                   ('fiscalyear_id', '=', fiscal.id)])
            for budget in budgets:
                expense_lines = BudgetLine.search([
                    ('id', 'in', budget.budget_expense_line_ids.ids),
                    ('charge_type', '=', 'internal')])
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
