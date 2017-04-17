# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .budget_plan_common import BPCommon, BPLCommon
from openerp.addons.account_budget_activity.models.account_activity \
    import ActivityCommon
from openerp.addons.document_status_history.models.document_history import \
    LogCommon


class BudgetPlanInvestConstruction(BPCommon, LogCommon, models.Model):
    _name = 'budget.plan.invest.construction'
    _inherit = ['mail.thread']
    _description = "Investment Construction Budget - Budget Plan"

    # COMMON
    plan_line_ids = fields.One2many(
        'budget.plan.invest.construction.line',
        'plan_id',
        string='Budget Plan Lines',
        copy=True,
        track_visibility='onchange',
    )
    plan_revenue_line_ids = fields.One2many(
        'budget.plan.invest.construction.line',
        'plan_id',
        string='Revenue Plan Lines',
        copy=True,
        domain=[('budget_method', '=', 'revenue')],  # Have domain
        track_visibility='onchange',
    )
    plan_expense_line_ids = fields.One2many(
        'budget.plan.invest.construction.line',
        'plan_id',
        string='Expense Plan Lines',
        copy=True,
        domain=[('budget_method', '=', 'expense')],  # Have domain
        track_visibility='onchange',
    )
    # --
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=True,
    )
    plan_line_ids = fields.One2many(
        'budget.plan.invest.construction.line',
        'plan_id',
        string='Budget Plan Lines',
        copy=True,
        track_visibility='onchange',
    )
    info_line_ids = fields.One2many(
        'budget.plan.invest.construction.line',
        'plan_id',
        string='Info Lines',
        copy=True,
        track_visibility='onchange',
    )
    extend_line_ids = fields.One2many(
        'budget.plan.invest.construction.line',
        'plan_id',
        string='Extended Lines',
        copy=True,
        track_visibility='onchange',
    )
    fy0_line_ids = fields.One2many(
        'budget.plan.invest.construction.line',
        'plan_id',
        string='FY0 Lines',
        copy=True,
        track_visibility='onchange',
    )


class BudgetPlanInvestConstructionLine(BPLCommon, ActivityCommon,
                                       models.Model):
    _name = 'budget.plan.invest.construction.line'
    _description = "Investment Construction Budget - Budget Plan Line"

    # COMMON
    chart_view = fields.Selection(
        default='invest_construction',  # Investment Construction
    )
    plan_id = fields.Many2one(
        'budget.plan.invest.construction',
        string='Budget Plan',
        ondelete='cascade',
        index=True,
        required=True,
    )
    # --
    invest_construction_id = fields.Many2one(
        related='invest_construction_phase_id.invest_construction_id',
        store=True,
        readonly=True,
    )
    c_or_n = fields.Selection(
        [('continue', 'Continue'),
         ('new', 'New')],
        string='C/N',
        default='new',
    )
    # From Project Construction Master Data
    date_start = fields.Date(
        string='Project Start Date',
    )
    date_end = fields.Date(
        string='Project End Date',
    )
    pm_employee_id = fields.Many2one(
        'hr.employee',
        string='Project Manager',
    )
    operation_area = fields.Char(
        string='Operation Area',
    )
    date_expansion = fields.Date(
        string='Expansion Date',
    )
    approval_info = fields.Text(
        string='Approval info',
    )
    project_readiness = fields.Text(
        string='Project Readiness',
    )
    reason = fields.Text(
        string='Reason',
    )
    expected_result = fields.Text(
        string='Expected Result',
    )
    phase_state = fields.Selection(
        [('draft', 'Draft'),
         ('submit', 'Submitted'),
         ('approve', 'Approved'),
         ('reject', 'Rejected'),
         ('delete', 'Deleted'),
         ('cancel', 'Cancelled'),
         ('close', 'Closed'),
         ],
        string='Phase Status',
    )
    phase_month_duration = fields.Integer(
        string='Duration (month)',
    )
    phase_date_start = fields.Date(
        string='Start Date',
    )
    phase_date_end = fields.Date(
        string='End Date',
    )
    amount_phase_plan = fields.Float(
        string='Budget',
    )
    amount_phase_plan_adj = fields.Float(
        string='Budget Adj',
    )
    amount_phase_actual = fields.Float(
        string='Actual',
    )
    amount_phase_diff = fields.Float(
        string='Balance',
    )
    amount_phase_plan_fy0 = fields.Float(
        string='FY0 (Prev)',
    )
    amount_phase_plan_fy1 = fields.Float(
        string='FY1 (Next)',
    )
    amount_phase_plan_fy2 = fields.Float(
        string='FY2',
    )
    amount_phase_plan_fy3 = fields.Float(
        string='FY3',
    )
    amount_phase_plan_fy4 = fields.Float(
        string='FY4',
    )
    amount_phase_plan_fy5 = fields.Float(
        string='FY5',
    )
    amount_phase_plan_fy6 = fields.Float(
        string='FY6 (Beyond)',
    )
    amount_fy0_released = fields.Float(
        string='FY0 Released',
    )
    amount_fy0_commit = fields.Float(
        string='FY0 Commit',
    )
    amount_fy0_exp_commit = fields.Float(
        string='FY0 EXP Commit',
    )
    amount_fy0_pr_commit = fields.Float(
        string='FY0 PR Commit',
    )
    amount_fy0_actual = fields.Float(
        string='FY0 Actual',
    )
    amount_fy0_consumed = fields.Float(
        string='FY0 Commit + Actual',
    )
    amoutn_fy0_balance = fields.Float(
        string='FY0 Balance',
    )

    @api.model
    def create(self, vals):
        res = super(BudgetPlanInvestConstructionLine, self).create(vals)
        res.update_related_dimension(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(BudgetPlanInvestConstructionLine, self).write(vals)
        if not self._context.get('MyModelLoopBreaker', False):
            self.update_related_dimension(vals)
        return res
