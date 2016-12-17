# -*- coding: utf-8 -*-
from openerp import models, api


class HRExpense(models.Model):
    _inherit = "hr.expense.expense"

    @api.model
    def _prepare_move_line(self, move, expense, name, analytic_account,
                           activity, debit=0.0, credit=0.0):
        result = super(HRExpense, self)._prepare_move_line(
            move, expense, name, analytic_account, activity, debit, credit)
        result.update(doc_ref=expense.number,
                      doc_id='%s,%s' % ('hr.expense.expense', expense.id))
        return result
