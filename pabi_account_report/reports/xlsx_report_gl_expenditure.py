# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PabiCommonAccountReportView(models.Model):
    _inherit = 'pabi.common.account.report.view'

    budget_fund_rule_ids = fields.Many2many(
        'budget.fund.rule.line',
        string='Budget Fund Rule Line',
        compute='_compute_budget_fund_rule_line',
    )

    @api.multi
    def _compute_budget_fund_rule_line(self):
        for rec in self:
            Fund = self.env['budget.fund.rule.line']
            domain = ([('fund_rule_id.fund_id', '=', rec.fund_id.id),
                       ('fund_rule_id.project_id', '=', rec.project_id.id),
                       ('fund_rule_id.state', '=', 'confirmed'),
                       ('account_ids', 'in', rec.account_id.id)])
            rec.budget_fund_rule_ids = Fund.search(domain)


class XLSXReportGlExpenditure(models.TransientModel):
    _name = 'xlsx.report.gl.expenditure'
    _inherit = 'report.account.common'

    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
    )
    activity_ids = fields.Many2many(
        'account.activity',
        string='Activitys',
    )
    activity_group_ids = fields.Many2many(
        'account.activity.group',
        string='Activitys',
    )
    date_posting = fields.Date(
        string='Posting Date',
    )
    filter = fields.Selection(
        default='filter_date',
        readonly=True,
    )
    fund_ids = fields.Many2many(
        'res.fund',
        string='Fund',
    )
    costcenter_ids = fields.Many2many(
        'res.costcenter',
        string='Costcenter',
    )
    results = fields.Many2many(
        'pabi.common.account.report.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['pabi.common.account.report.view']
        dom = [('account_id.user_type.code', '=', 'Expense'),
               ('project_id', '!=', False)]
        if self.account_ids:
            dom += [('account_id', 'in', self.account_ids.ids)]
        if self.activity_ids:
            dom += [('activity_id', 'in', self.activity_ids.ids)]
        if self.activity_group_ids:
            dom += [('activity_group_id', 'in', self.activity_group_ids.ids)]
        if self.date_posting:
            dom += [('invoice_move_line_id.date', '=', self.date_posting)]
        if self.fund_ids:
            dom += [('fund_id', 'in', self.fund_ids.ids)]
        if self.costcenter_ids:
            dom += [('costcenter_id', 'in', self.costcenter_ids.ids)]
        self.results = Result.search(dom)
