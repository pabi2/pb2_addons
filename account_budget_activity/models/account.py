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

    @api.onchange('budget_control')
    def _onchange_budget_control(self):
        AccountBudget = self.env['account.budget']
        BudgetLevel = self.env['account.fiscalyear.budget.level']
        if not self.budget_level_ids:
            for level_type in AccountBudget.BUDGET_LEVEL_TYPE.items():
                budget_level = BudgetLevel.new()
                budget_level.type = level_type[0]
                self.budget_level_ids += budget_level


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
        required=True,
        default='activity_group_id',
    )
