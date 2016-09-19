# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    account_deposit_supplier = fields.Many2one(
        'account.account',
        string='Supplier Advance Account',
        domain=[('type', '!=', 'view')],
    )
