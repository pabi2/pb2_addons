# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def confirm_paid(self):
        expenses = self.env['hr.expense.expense'].search([('invoice_id',
                                                           'in', self._ids)])
        history_obj = self.env['hr.expense.advance.due.history']
        for expense in expenses:
            if not expense.is_employee_advance:
                continue
            date_due = False
            # Case 1) buy_product, date_due = paid_date + 30 days
            if expense.advance_type == 'buy_product':
                date_paid = expense.invoice_id.payment_ids[0].date
                date_due = (datetime.strptime(date_paid, '%Y-%m-%d') +
                            relativedelta(days=30))
            # Case 2) attend_seminar, date_due = arrive date + 30 days
            elif expense.advance_type == 'attend_seminar':
                date_back = expense.date_back
                date_due = (datetime.strptime(date_back, '%Y-%m-%d') +
                            relativedelta(days=30))
            else:
                raise UserError(_('Can not calculate due date. '
                                  'No Advance Type vs Due Date Rule'))
            if date_due:
                history_obj.create({
                    'expense_id': expense.id,
                    'date_due': date_due.strftime('%Y-%m-%d'),
                })
        return super(AccountInvoice, self).confirm_paid()
