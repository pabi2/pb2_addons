# -*- coding: utf-8 -*-
# © 2016 Kitti U.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields, _


class EmployeeMessage(models.TransientModel):
    _name = "employee.message"

    message = fields.Text(
        string='Message',
        required=True
    )

    @api.multi
    def action_send_message(self):
        self.ensure_one()
        ExpenseObj = self.env['hr.expense.expense']
        expense_ids = self._context.get('active_ids', [])
        for expense in ExpenseObj.browse(expense_ids):
            expense.message_post(body=self.message, type='notification')
