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
    loan_income_activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Income Activity Group',
    )
    loan_income_activity_id = fields.Many2one(
        'account.activity',
        string='Income Activity',
        domain="[('activity_group_ids', 'in',"
               "[loan_income_activity_group_id or -1])]",
    )
    loan_income_account_id = fields.Many2one(
        'account.account',
        string='Income Account',
        domain=[('type', '=', 'other'),
                ('user_type.report_type', '=', 'income')],
    )
    loan_force_close_account_id = fields.Many2one(
        'account.account',
        string='Force Close Account',
    )
