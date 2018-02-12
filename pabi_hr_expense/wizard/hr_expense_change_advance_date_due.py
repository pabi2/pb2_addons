# -*- coding: utf-8 -*-
from openerp import models, fields, api


class HRExpenseChangeAdvanceDateDue(models.TransientModel):
    _name = "hr.expense.change.advance.date.due"

    expense_id = fields.Many2one(
        'hr.expense.expense',
        string='Expense',
        default=lambda self: self._context.get('active_id', False),
    )
    date_due = fields.Date(
        string='Due Date',
    )

    @api.multi
    def change_advance_date_due(self):
        self.ensure_one()
        history_obj = self.env['hr.expense.advance.due.history']
        if self.date_due:
            history_obj.create({
                'expense_id': self.expense_id.id,
                'date_old_due': self.expense_id.date_due,
                'date_due': self.date_due,
            })
