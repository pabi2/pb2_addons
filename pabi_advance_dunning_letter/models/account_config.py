# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    group_email = fields.Char(
        string='Group Email',
        related='company_id.group_email',
    )
    head_account_employee_id = fields.Many2one(
        'hr.employee',
        string='Head Accounting',
        related='company_id.head_account_employee_id',
    )
