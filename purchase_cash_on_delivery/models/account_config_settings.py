# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    prepaid_account_id = fields.Many2one(
        'account.account',
        string='Prepaid Account',
        related="company_id.prepaid_account_id",
    )
