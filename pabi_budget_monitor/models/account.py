# -*- coding: utf-8 -*-
from openerp import models
from openerp import SUPERUSER_ID
from openerp.api import Environment


class AccountFiscalyear(models.Model):
    _inherit = 'account.fiscalyear'

    def init(self, cr):
        env = Environment(cr, SUPERUSER_ID, {})
        fiscalyears = env['account.fiscalyear'].search([])
        fiscalyears.create_budget_level_config()
