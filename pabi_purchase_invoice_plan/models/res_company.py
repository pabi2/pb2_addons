# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    other_deposit_account_ids = fields.Many2many(
        'account.account',
        string='Other Advance Accounts',
        domain=[('type', '!=', 'view')],
        help="Lst other eligible for user to choose manually on document",
    )
