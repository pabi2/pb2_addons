# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountFiscalyear(models.Model):
    _inherit = 'account.fiscalyear'

    budget_control = fields.Boolean(
        string='Budget Control',
        default=False,
    )
    budget_level_ids = fields.One2many(
        'account.fiscalyear.budget.level',
        'fiscal_id',
        string='Budgeting Level',
    )

    @api.multi
    def create_budget_level_config(self):
        AccountBudget = self.env['account.budget']
        BudgetLevel = self.env['account.fiscalyear.budget.level']
        budget_levels = AccountBudget.BUDGET_LEVEL_TYPE.items()
        for rec in self:
            if len(rec.budget_level_ids) != len(budget_levels):
                rec.budget_level_ids = False
                for level_type in AccountBudget.BUDGET_LEVEL_TYPE.items():
                    budget_level = BudgetLevel.new()
                    budget_level.type = level_type[0]
                    rec.budget_level_ids += budget_level


class AccountFiscalyearBudgetLevel(models.Model):
    _name = 'account.fiscalyear.budget.level'

    fiscal_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal',
        readonly=True,
    )
    type = fields.Selection(
        lambda self: self.env['account.budget'].BUDGET_LEVEL_TYPE.items(),
        string='Type',
        required=True,
        readonly=True,
    )
    budget_level = fields.Selection(
        lambda self: self.env['account.budget'].BUDGET_LEVEL.items(),
        string='Budget Level',
        required=False,
    )
    is_budget_control = fields.Boolean(
        string='Control',
        default=False,
    )
#     pr_budget_control = fields.Boolean(
#         string='Control on PR',
#         default=False,
#     )
#     po_budget_control = fields.Boolean(
#         string='Control on PO',
#         default=False,
#     )
#     exp_budget_control = fields.Boolean(
#         string='Control on Expense',
#         default=False,
#     )
    release_interval = fields.Selection(
        [('1', '1 Month'),
         ('3', '3 Months'),
         ('6', '6 Months'),
         ('12', '12 Months'), ],
        string='Budget Release Interval',
        default='1'
    )
    is_auto_release = fields.Boolean(
        string='Auto Release',
        default=False,
    )


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_budget_commit = fields.Boolean(
        string='Commit Budget',
        default=False,
    )
    pr_commitment_analytic_journal_id = fields.Many2one(
        'account.analytic.journal',
        string='Analytic Journal for PR Commitments',
        domain=[('type', '=', 'general')]
    )
    pr_commitment_account_id = fields.Many2one(
        'account.account',
        string='Account for PR Commitment',
        domain=[('type', '!=', 'view')]
    )
    po_commitment_analytic_journal_id = fields.Many2one(
        'account.analytic.journal',
        string='Analytic Journal for PO Commitments',
        domain=[('type', '=', 'general')]
    )
    po_commitment_account_id = fields.Many2one(
        'account.account',
        string='Account for PO Commitment',
        domain=[('type', '!=', 'view')]
    )
    exp_commitment_analytic_journal_id = fields.Many2one(
        'account.analytic.journal',
        string='Analytic Journal for Expense Commitments',
        domain=[('type', '=', 'general')]
    )
    exp_commitment_account_id = fields.Many2one(
        'account.account',
        string='Account for Expense Commitment',
        domain=[('type', '!=', 'view')]
    )
