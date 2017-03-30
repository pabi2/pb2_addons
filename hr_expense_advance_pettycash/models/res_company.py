# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    employee_pettycash_account_id = fields.Many2one(
        'account.account',
        string='Petty Cash Account',
        domain=[('type', '!=', 'view')],
    )
