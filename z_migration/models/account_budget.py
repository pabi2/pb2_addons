# -*- coding: utf-8 -*-
from openerp import models, api


class AccountBudget(models.Model):
    _inherit = 'account.budget'

    @api.multi
    def mork_budget_done(self):
        self.budget_done()
        return True
