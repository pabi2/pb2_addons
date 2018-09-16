# -*- coding: utf-8 -*-
from openerp import api, models, fields


class EmployeeMessage(models.TransientModel):
    _name = 'employee.message'

    message = fields.Text(
        string='Message',
        required=True,
        size=1000,
    )

    @api.multi
    def action_send_message(self):
        self.ensure_one()
        ExpenseObj = self.env['hr.expense.expense']
        expense_ids = self._context.get('active_ids', [])
        for expense in ExpenseObj.browse(expense_ids):
            expense.message_post(body=self.message, type='notification')
