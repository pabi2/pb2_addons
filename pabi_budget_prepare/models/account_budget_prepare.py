# -*- coding: utf-8 -*-
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class AccountBudgetPrepare(models.Model):
    _name = "account.budget.prepare"
    _description = "Budget Prepare"

    name = fields.Char(
        string='Name',
        required=True,
        states={'published': [('readonly', True)]},
    )
    code = fields.Char(
        string='Code',
        size=16,
        required=True,
        states={'published': [('readonly', True)]},
    )
    creating_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self._uid,
    )
    validating_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
    )
    date_from = fields.Date(
        string='Start Date',
        compute='_compute_date',
        readonly=True,
        store=True,
    )
    date_to = fields.Date(
        string='Start Date',
        compute='_compute_date',
        readonly=True,
        store=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    state = fields.Selection(
        [('plan', 'Plan'),
         ('cancel', 'Cancelled'),
         ('policy', 'Policy'),
         ('release', 'Release'),
         ('publish', 'Published')],
        string='Status',
        default='plan',
        index=True,
        required=True,
        readonly=True,
        copy=False,
    )
    prepare_line_ids = fields.One2many(
        'account.budget.prepare.line',
        'prepare_id',
        string='Budget Prepare Lines',
        states={'publish': [('readonly', True)]},
        copy=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env[
            'res.company']._company_default_get('account.budget')
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
    )

    @api.one
    @api.depends('fiscalyear_id')
    def _compute_date(self):
        self.date_from = self.fiscalyear_id.date_start
        self.date_to = self.fiscalyear_id.date_stop

    @api.multi
    def budget_release(self):
        self.write({
            'state': 'release',
            'validating_user_id': self._uid,
        })
        return True

    @api.multi
    def budget_policy(self):
        self.write({'state': 'policy'})
        return True

    @api.multi
    def budget_plan(self):
        self.write({'state': 'plan'})
        return True

    @api.multi
    def budget_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def budget_publish(self):
        self.write({'state': 'publish'})
        return True


class AccountBudgetPrepareLine(models.Model):

    _name = "account.budget.prepare.line"
    _description = "Budget Line"

    prepare_id = fields.Many2one(
        'account.budget.prepare',
        string='Budget Prepare',
        ondelete='cascade',
        index=True,
        required=True,
    )
    company_id = fields.Many2one(
        'res.company',
        related='prepare_id.company_id',
        string='Company',
        type='many2one',
        store=True,
        readonly=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    # TODO: Add more Project dimensions
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group',
    )
    program_id = fields.Many2one(
        'res.program',
        string='Program',
    )
    project_group_id = fields.Many2one(
        'res.project.group',
        string='Project Group',
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        digits_compute=dp.get_precision('Account'),
    )
    # Monetary
    revenue_planned = fields.Float(
        string='Revenue Planned',
        digits_compute=dp.get_precision('Account'),
    )
    revenue_to_date = fields.Float(
        string='Revenue Actual',
        digits_compute=dp.get_precision('Account'),
    )
    revenue_this_year = fields.Float(
        string='Revenue Actual (this year)',
        digits_compute=dp.get_precision('Account'),
    )
    total_budget_planned = fields.Float(
        string='Total Budget Planned',
        digits_compute=dp.get_precision('Account'),
    )
    total_budget_expense = fields.Float(
        string='Total Expense',
        digits_compute=dp.get_precision('Account'),
    )
    total_budget_commit = fields.Float(
        string='Total Commitment',
        digits_compute=dp.get_precision('Account'),
    )
    total_budget_balance = fields.Float(
        string='Total Balance',
        digits_compute=dp.get_precision('Account'),
    )
    yearly_budget_current = fields.Float(
        string='Yearly Budget Current',
        digits_compute=dp.get_precision('Account'),
    )
    yearly_budget_release = fields.Float(
        string='Yearly Budget Release',
        digits_compute=dp.get_precision('Account'),
    )
    yearly_budget_commit = fields.Float(
        string='Yearly Commitment',
        digits_compute=dp.get_precision('Account'),
    )
    yearly_budget_expense = fields.Float(
        string='Yearly Expense',
        digits_compute=dp.get_precision('Account'),
    )
    yearly_budget_balance = fields.Float(
        string='Yearly Balance',
        digits_compute=dp.get_precision('Account'),
    )
    amount_fy1_q1 = fields.Float(
        string='FY1/Q1',
        digits_compute=dp.get_precision('Account'),
    )
    amount_fy1_q2 = fields.Float(
        string='FY1/Q2',
        digits_compute=dp.get_precision('Account'),
    )
    amount_fy1_q3 = fields.Float(
        string='FY1/Q3',
        digits_compute=dp.get_precision('Account'),
    )
    amount_year1_q4 = fields.Float(
        string='FY1/Q4',
        digits_compute=dp.get_precision('Account'),
    )
    amount_fy1 = fields.Float(
        string='FY1',
        digits_compute=dp.get_precision('Account'),
    )
    amount_fy2 = fields.Float(
        string='FY2',
        digits_compute=dp.get_precision('Account'),
    )
    amount_fy3 = fields.Float(
        string='FY3',
        digits_compute=dp.get_precision('Account'),
    )
    amount_fy4 = fields.Float(
        string='FY4',
        digits_compute=dp.get_precision('Account'),
    )
    amount_fy5 = fields.Float(
        string='FY5',
        digits_compute=dp.get_precision('Account'),
    )
    amount_total = fields.Float(
        string='Amount Total',
        digits_compute=dp.get_precision('Account'),
    )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
