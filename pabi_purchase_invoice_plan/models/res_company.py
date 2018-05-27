# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    other_deposit_account_ids = fields.Many2many(
        'account.account',
        'company_deposit_account_rel',
        'company_id', 'deposit_account_id',
        string='Other Advance Accounts',
        domain=[('type', '!=', 'view')],
        help="Lst other eligible for user to choose manually on document",
    )
