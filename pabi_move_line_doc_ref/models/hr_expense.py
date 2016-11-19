# -*- coding: utf-8 -*-
from openerp import models, api


class HRExpense(models.Model):
    _inherit = "hr.expense.expense"

    @api.model
    def _prepare_move_line(self, move, expense_line, analytic_account,
                           activity, debit=0.0, credit=0.0):
        result = super(HRExpense, self)._prepare_move_line(
            move, expense_line, analytic_account, activity, debit, credit)
        result.update(doc_ref=expense_line.expense_id.number,
                      doc_id='%s,%s' % ('hr.expense.expense',
                                        expense_line.expense_id.id))
        return result
