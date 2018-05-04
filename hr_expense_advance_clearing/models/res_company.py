# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    employee_advance_account_id = fields.Many2one(
        'account.account',
        string='Employee Advance Account',
        domain=[('type', '!=', 'view')],
    )
