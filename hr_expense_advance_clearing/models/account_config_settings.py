# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    employee_advance_product_id = fields.Many2one(
        'product.product',
        string='Employee Advance Product',
        related="company_id.employee_advance_product_id",
    )
