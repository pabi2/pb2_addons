# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    account_tax_difference = fields.Many2one(
        'account.account',
        string='Tax Difference Account',
        related="company_id.account_tax_difference",
    )
    number_month_tax_addition = fields.Integer(
        string='Number of months for additional Tax',
        related="company_id.number_month_tax_addition",
    )
