# -*- coding: utf-8 -*-
from openerp import api, models
from openerp.exceptions import Warning as UserError


class HRExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.multi
    def _expense_budget_check(self):
        Budget = self.env['account.budget']
        for expense in self:
            if expense.is_employee_advance:  # For AV, no budget check
                continue
            doc_date = expense.date
            doc_lines = Budget.convert_lines_to_doc_lines(expense.line_ids)
            res = Budget.post_commit_budget_check(doc_date, doc_lines)
            if not res['budget_ok']:
                raise UserError(res['message'])
        return True

    @api.multi
    def write(self, vals):
        res = super(HRExpenseExpense, self).write(vals)
        # Commit budget as soon as Draft (approved by AP Web), so budget check
        if vals.get('state', False) == 'draft':
            self._expense_budget_check()
        return res
