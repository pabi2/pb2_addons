# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    employee_advance_product_id = fields.Many2one(
        'product.product',
        string='Employee Advance Product',
        domain=[('hr_expense_ok', '=', True)],
    )
