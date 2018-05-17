# -*- coding: utf-8 -*-
from openerp import models, api


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.model
    def _post_process_hr_expense(self, expense):
        if expense.internal_charge:  # Case internal charge
            expense.signal_workflow('internal_charge')
        else:
            super(HRExpense, self)._post_process_hr_expense(expense)
