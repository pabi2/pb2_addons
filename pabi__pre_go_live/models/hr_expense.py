# -*- coding: utf-8 -*-
from openerp import models, fields


class HRExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    amount_advanced = fields.Float(
        string='Advanced Amount',
        readonly=False,
    )
