# -*- coding: utf-8 -*-
from openerp import api, models
from openerp.exceptions import Warning as UserError


class HRExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.multi
    def _expense_budget_check(self):
        Budget = self.env['account.budget']
        for expense in self:
            doc_date = expense.date
            doc_lines = Budget.convert_lines_to_doc_lines(expense.line_ids)
            res = Budget.document_check_budget(doc_date,
                                               doc_lines,
                                               'total_amount')
            if not res['budget_ok']:
                raise UserError(res['message'])
        return True
