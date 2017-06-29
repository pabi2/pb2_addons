# -*- coding: utf-8 -*-
from openerp import models, fields


class HRExpenseExpense(models.Model):
    _inherit = "hr.expense.expense"
    _rec_name = "number"

    is_employee_pettycash = fields.Boolean(
        string='Petty Cash',
        default=False,
    )
