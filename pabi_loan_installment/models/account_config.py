# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    loan_installment_account_id = fields.Many2one(
        'account.account',
        string='Loan Installment Account',
        related="company_id.loan_installment_account_id",
    )
    loan_defer_income_account_id = fields.Many2one(
        'account.account',
        string='Defer Income Account',
        related="company_id.loan_defer_income_account_id",
    )
    loan_income_activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Income Activity Group',
        related="company_id.loan_income_activity_group_id",
    )
    loan_income_activity_id = fields.Many2one(
        'account.activity',
        string='Income Activity',
        related="company_id.loan_income_activity_id",
    )
    loan_income_account_id = fields.Many2one(
        'account.account',
        string='Income Account',
        related="company_id.loan_income_account_id",
    )
    loan_force_close_account_id = fields.Many2one(
        'account.account',
        string='Force Close Account',
        related="company_id.loan_force_close_account_id",
    )

    @api.onchange('loan_income_activity_id')
    def _onchange_loan_income_activity_id(self):
        self.loan_income_account_id = self.loan_income_activity_id.account_id
