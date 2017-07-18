# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.api import Environment
from openerp import SUPERUSER_ID


class AccountFiscalyearBudgetLevel(models.Model):
    _inherit = 'account.fiscalyear.budget.level'

    release_follow_policy = fields.Boolean(
        string='Release by Policy',
        default=False,
        help="Change released amount with policy amount",
    )

    @api.onchange('budget_release')
    def _onchange_budget_release(self):
        self.release_follow_policy = False


class AccountFiscalyear(models.Model):
    _inherit = 'account.fiscalyear'

    budget_allocation_ids = fields.One2many(
        'budget.allocation',
        'fiscalyear_id',
        string='Budget Allocations',
    )

    def init(self, cr):
        env = Environment(cr, SUPERUSER_ID, {})
        Fiscal = env['account.fiscalyear']
        fiscals = Fiscal.search([])
        fiscals.generate_budget_allocations()

    @api.multi
    def generate_budget_allocations(self):
        for fiscal in self:
            if not fiscal.budget_allocation_ids:
                lines = [(0, 0, {'revision': str(i)}) for i in range(13)]
                fiscal.write({'budget_allocation_ids': lines})

    @api.model
    def create(self, vals):
        fiscal = super(AccountFiscalyear, self).create(vals)
        fiscal.generate_budget_allocations()
        return fiscal
