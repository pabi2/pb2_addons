# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    prepaid_account_id = fields.Many2one(
        'account.account',
        string='Prepaid Account',
        domain=[('type', '!=', 'view')],
    )
