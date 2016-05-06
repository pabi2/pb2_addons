# -*- coding: utf-8 -*-
from openerp import fields, models


class HrExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    operating_unit_id = fields.Many2one(required=True)
