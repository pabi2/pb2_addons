# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportBudgetSummary(models.TransientModel):
    _name = 'xlsx.report.budget.summary'
    _inherit = 'xlsx.report'

    # Search Criteria
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
    )
    # Report Result
    results = fields.Many2many(
        'xlsx.report.budget.summary.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.budget.summary.results']
        self.results = Result.search([
            ('fiscalyear_id', '=', self.fiscalyear_id.id)])


class XLSXReportBudgetSummaryResults(models.Model):
    _name = 'xlsx.report.budget.summary.results'
    _auto = False
    _description = 'Temp table as ORM holder'

    chart_view = fields.Selection(
        [('personnel', 'Personnel'),
         ('invest_asset', 'Investment Asset'),
         ('unit_base', 'Unit Based'),
         ('project_base', 'Project Based'),
         ('invest_construction', 'Investment Construction')],
        string='Budget View',
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        readonly=True,
    )
    plan = fields.Float(
        string='Planned Amount',
        readonly=True,
    )
    policy = fields.Float(
        string='Policy Amount',
        readonly=True,
    )
    released = fields.Float(
        string='Released Amount',
        readonly=True,
    )
    pr_commit = fields.Float(
        string='PR Commitment',
        readonly=True,
    )
    po_commit = fields.Float(
        string='PO Commitment',
        readonly=True,
    )
    exp_commit = fields.Float(
        string='Expense Commitment',
        readonly=True,
    )
    actual_total = fields.Float(
        string='Actual',
        readonly=True,
    )
    balance = fields.Float(
        string='Balance',
        readonly=True,
    )
    actual_percent = fields.Float(
        string='Actual Percent',
        readonly=True,
    )
    commit_total = fields.Float(
        string='Commit Total',
        readonly=True,
    )
    commit_percent = fields.Float(
        string='Commit Percent',
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            select row_number() over (order by rpt.chart_view,
                                               rpt.fiscalyear_id) as id,
                   rpt.chart_view, rpt.fiscalyear_id,
                   coalesce(plan, 0.0) as plan,
                   (select coalesce(sum(policy_amount), 0.0)
                    from budget_policy
                    where fiscalyear_id = rpt.fiscalyear_id
                    and chart_view = rpt.chart_view) as policy,
                   coalesce(released, 0.0) as released,
                   coalesce(pr_commit, 0.0) as pr_commit,
                   coalesce(po_commit, 0.0) as po_commit,
                   coalesce(exp_commit, 0.0) as exp_commit,
                   coalesce(actual_total, 0.0) as actual_total,
                   coalesce(balance, 0.0) as balance,
                   coalesce(total, 0.0) as commit_and_actual,
                   case when total = 0 then 0
                    else (actual_total/total) * 100 end as actual_percent,
                   coalesce(pr_commit+po_commit+exp_commit, 0.0)
                    as commit_total,
                   case when total = 0 then 0 else
                    coalesce(pr_commit+po_commit+exp_commit, 0.0)/total * 100
                    end as commit_percent
            from
                   (select chart_view, fiscalyear_id,
                           sum(planned_amount) as plan,
                           sum(released_amount) as released,
                           sum(amount_pr_commit) as pr_commit,
                           sum(amount_po_commit) as po_commit,
                           sum(amount_exp_commit) as exp_commit,
                           sum(amount_actual) as actual_total,
                           sum(amount_balance) as balance,
                           sum(amount_consumed) as total
                    from budget_monitor_report
                    where budget_method = 'expense'
                    group by chart_view, fiscalyear_id) rpt)""" % self._table)
