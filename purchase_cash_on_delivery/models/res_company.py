# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    prepaid_account_ids = fields.Many2many(
        'account.account',
        'company_prepaid_account_rel',
        'company_id', 'perpaid_account_id',
        string='Prepaid Accounts',
        domain=[('type', '!=', 'view')],
        help="List of accounts for prepayment",
    )
