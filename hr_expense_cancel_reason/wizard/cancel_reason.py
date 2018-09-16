# -*- coding: utf-8 -*-

from openerp import models, fields, api


class HRExpenseCancel(models.TransientModel):

    """ Ask a reason for the hr expense cancellation."""
    _name = 'hr.expense.cancel'
    _description = __doc__

    cancel_reason_txt = fields.Char(
        string="Reason",
        size=500,
    )

    @api.one
    def confirm_cancel(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        expense_ids = self._context.get('active_ids')
        if expense_ids is None:
            return act_close
        assert len(expense_ids) == 1, "Only 1 Expense ID expected"
        expense = self.env['hr.expense.expense'].browse(expense_ids)
        expense.cancel_reason_txt = self.cancel_reason_txt
        expense.signal_workflow('refuse')
        return act_close
