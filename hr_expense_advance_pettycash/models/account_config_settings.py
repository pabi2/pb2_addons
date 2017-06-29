# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    employee_pettycash_account_id = fields.Many2one(
        'account.account',
        string='Petty Cash Account',
        related="company_id.employee_pettycash_account_id",
    )
