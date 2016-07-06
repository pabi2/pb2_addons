# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, api, fields, _
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    is_diff_expense_amount = fields.Boolean(
        string='Amount different from expense',
        compute='_compute_is_diff_expense_amount',
    )
    diff_expense_amount_reason = fields.Char(
        string='Amount Diff Reason',
        help="Reason when amount is different from Expense",
    )

    @api.multi
    @api.depends('amount_total')
    def _compute_is_diff_expense_amount(self):
        for rec in self:
            rec.is_diff_expense_amount = False
            if self.expense_id:
                clear_amount = sum([x.price_subtotal < 0.0 and
                                    x.price_subtotal or 0.0
                                    for x in self.invoice_line])
                amount = self.amount_total - clear_amount
                if amount != self.expense_id.amount:
                    rec.is_diff_expense_amount = True

    @api.one
    @api.constrains('amount_total')
    def _check_amount_not_over_expense(self):
        # For expense related invoice
        # Positive line amount must not over total expense
        if self.expense_id:
            # Negative amount is advance clearing
            clear_amount = sum([x.price_subtotal < 0.0 and
                                x.price_subtotal or 0.0
                                for x in self.invoice_line])
            amount = self.amount_total - clear_amount
            if amount > self.expense_id.amount:
                raise UserError(_('New amount over expense is not allowed!'))

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
