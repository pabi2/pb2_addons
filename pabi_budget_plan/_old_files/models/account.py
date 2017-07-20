# -*- coding: utf-8 -*-
from openerp import models, fields, api


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
