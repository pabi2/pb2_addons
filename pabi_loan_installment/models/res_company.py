# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    loan_installment_account_id = fields.Many2one(
        'account.account',
        string='Locan Installment Account',
    )
