# -*- coding: utf-8 -*-
from openerp import models, fields


class ResDoctype(models.Model):
    _inherit = 'res.doctype'

    refer_type = fields.Selection(
        selection_add=[
            ('employee_expense', 'Employee Expense'),
            ('employee_advance', 'Employee Advance'),
        ],
    )
