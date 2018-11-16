# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    prepaid_account_ids = fields.Many2many(
        'account.account',
        string='Prepaid Accounts',
        related='company_id.prepaid_account_ids',
        help="List of accounts for prepayment",
    )
