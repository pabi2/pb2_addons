# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    loan_penalty_product_id = fields.Many2one(
        'product.product',
        string='Loan Penalty Product',
        related="company_id.loan_penalty_product_id",
    )
