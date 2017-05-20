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
                    # budget_level.release_interval = False
                    rec.budget_level_ids += budget_level

    @api.multi
    def get_fiscal_month_vs_period(self):
        """ return {peirod: month, ...}, as {1: 10, ... 12: 9} """
        self.ensure_one()
        month = int(self.date_start[5:7])
        result = {}
        for i in range(12):
            result[month] = i + 1
            month += 1
            if month > 12:
                month = 1
        return result

    @api.multi
    def _get_budget_level(self, ttype='check_budget'):
        """
        Get budget level by fiscalyear.
        If type not specified, use 'check_budget', which is default type.
        """
        self.ensure_one()
        budget_level = self.budget_level_ids.filtered(
            lambda l: l.type == ttype)
        return budget_level


class AccountFiscalyearBudgetLevel(models.Model):
    _name = 'account.fiscalyear.budget.level'
    _rec_name = 'budget_level'

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
    budget_release = fields.Selection(
        [('manual_line', 'Budget Line'),
         ('manual_header', 'Budget Header'),
         ('auto', 'Auto Release as Planned'), ],
        string='Release Type',
        default='manual_line',
        required=True,
    )
    check_plan_with_released_amount = fields.Boolean(
        help="When confirm budget control, check that sum "
        "planned amount not exceed the released amount"
    )


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
