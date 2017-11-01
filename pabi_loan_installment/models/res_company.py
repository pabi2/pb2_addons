# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    loan_installment_account_id = fields.Many2one(
        'account.account',
        string='Locan Installment Account',
    )
    loan_defer_income_account_id = fields.Many2one(
        'account.account',
        string='Income Account',
        domain=[('type', '=', 'other'),
                ('user_type.report_type', '=', 'liability')],
    )
    loan_income_account_id = fields.Many2one(
        'account.account',
        string='Income Account',
        domain=[('type', '=', 'other'),
                ('user_type.report_type', '=', 'income')],
    )
