# -*- coding: utf-8 -*-
from openerp import api, models


class HRExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.multi
    def _expense_budget_check(self):
        Budget = self.env['account.budget']
        for expense in self:
            active_id = expense.id
            # Get budget level type resources
            budget_level_info = Budget.\
                get_fiscal_and_budget_level(expense.date)
            fiscal_id = budget_level_info['fiscal_id']
            Budget.document_check_budget(expense.line_ids,
                                         'total_amount',
                                         budget_level_info,
                                         fiscal_id, active_id)
        return True
