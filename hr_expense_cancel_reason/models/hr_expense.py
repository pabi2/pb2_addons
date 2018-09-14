# -*- coding: utf-8 -*-

from openerp import models, fields


class HRExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    cancel_reason_txt = fields.Char(
        string="Description",
        readonly=True,
        size=500,
    )
