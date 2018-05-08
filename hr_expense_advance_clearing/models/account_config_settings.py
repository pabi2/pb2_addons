# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    employee_advance_account_id = fields.Many2one(
        'account.account',
        string='Employee Advance Account',
        related="company_id.employee_advance_account_id",
    )
