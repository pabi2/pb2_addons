# -*- coding: utf-8 -*-
from openerp import fields, models, api
from .account_activity import ActivityCommon


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
                    budget_level.release_interval = False
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
    exp_budget_control = fields.Boolean(
        string='Control on Expense',
        default=False,
    )
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

    @api.onchange('is_budget_control')
    def onchange_is_budget_control(self):
        for record in self:
            record.exp_budget_control = record.is_budget_control


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_budget_commit = fields.Boolean(
        string='Commit Budget',
        default=False,
    )
    so_commitment_analytic_journal_id = fields.Many2one(
        'account.analytic.journal',
        string='Analytic Journal for SO Commitments',
        domain=[('type', '=', 'general')]
    )
    so_commitment_account_id = fields.Many2one(
        'account.account',
        string='Account for SO Commitment',
        domain=[('type', '!=', 'view')]
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


class AccountAccount(models.Model):
    _inherit = 'account.account'

    activity_ids = fields.One2many(
        'account.activity',
        'account_id',
        string='Activities',
        readonly=True,
    )


class AccountModelLine(ActivityCommon, models.Model):
    _inherit = 'account.model.line'

    @api.model
    def create(self, vals):
        line = super(AccountModelLine, self).create(vals)
        Analytic = self.env['account.analytic.account']
        line.analytic_account_id = \
            Analytic.create_matched_analytic(line)
        return line

    @api.multi
    def write(self, vals):
        res = super(AccountModelLine, self).write(vals)
        if self.env.context.get('MyModelLoopBreaker'):
            return res
        self = self.with_context(MyModelLoopBreaker=True)
        for line in self:
            Analytic = self.env['account.analytic.account']
            line.analytic_account_id = \
                Analytic.create_matched_analytic(line)
        return res
