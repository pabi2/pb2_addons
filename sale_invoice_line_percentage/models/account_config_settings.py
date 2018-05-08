# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    account_deposit_customer = fields.Many2one(
        'account.account',
        string='Customer Advance Account',
        related="company_id.account_deposit_customer",
    )
