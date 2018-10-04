# -*- coding: utf-8 -*-
from openerp import models, api, SUPERUSER_ID
from .common import DoclineCommon, DoclineCommonSeq


class HRExpense(DoclineCommon, models.Model):
    _inherit = 'hr.expense.expense'

    @api.multi
    @api.constrains('line_ids')
    def _check_docline_seq(self):
        for order in self:
            self._compute_docline_seq('hr_expense_line',
                                      'expense_id', order.id)
        return True


class HRExpenseLine(DoclineCommonSeq, models.Model):
    _inherit = 'hr.expense.line'

    def init(self, cr):
        """ On module update, recompute all documents """
        self.pool.get('hr.expense.expense').\
            _recompute_all_docline_seq(cr, SUPERUSER_ID,
                                       'hr_expense_expense',
                                       'hr_expense_line',
                                       'expense_id')
