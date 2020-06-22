# -*- coding: utf-8 -*-
from openerp import api, models
from openerp.exceptions import ValidationError


class HRExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.multi
    def _expense_budget_check(self):
        Budget = self.env['account.budget']
        for expense in self:
            ctx = {}
            fiscal_id, budget_levels = \
                Budget.get_fiscal_and_budget_level(expense.date)
            fiscal = self.env['account.fiscalyear'].browse(fiscal_id)
            if expense.is_employee_advance:
                continue
            doc_date = expense.date
            doc_lines = Budget.convert_lines_to_doc_lines(expense.line_ids)
            if expense.pay_to == 'internal' and fiscal.control_ext_charge_only:
                ctx = {'force_no_budget_check': True}
            res = Budget.with_context(ctx).post_commit_budget_check(
                doc_date, doc_lines)
            if not res['budget_ok']:
                raise ValidationError(res['message'])
        return True

    @api.multi
    def write(self, vals):
        res = super(HRExpenseExpense, self).write(vals)
        # Commit budget as soon as Draft (approved by AP Web), so budget check
        if vals.get('state', False) == 'draft':
            self._expense_budget_check()
        return res
