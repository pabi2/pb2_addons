# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    longterm_invest_account_id = fields.Many2one(
        'account.account',
        string='Long Term Investment Account',
        related="company_id.longterm_invest_account_id",
    )
