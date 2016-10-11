# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, api, fields, _
from openerp.exceptions import Warning as UserError
from openerp.tools import float_compare


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    amount_expense_request = fields.Float(
        string='Expense Request Amount',
        copy=False,
        readonly=True,
    )
    diff_expense_amount_flag = fields.Integer(
        string='Amount different from expense',
        compute='_compute_diff_expense_amount_flag',
        readonly=True,
        default=0,
        help="""
        * Flat = 0 when amount invoice = amount expense\n
        * Flag = 1 when amount invoice > amount expense.\n
        * Flag = -1 when amount invoice < amount expense.
        """
    )
    diff_expense_amount_reason = fields.Char(
        string='Amount Diff Reason',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Reason when amount is different from Expense",
    )

    @api.multi
    @api.depends('amount_total')
    def _compute_diff_expense_amount_flag(self):
        for rec in self:
            if rec.expense_id:
                rec.diff_expense_amount_flag = 0
                clear_amount = sum([x.price_subtotal < 0.0 and
                                    x.price_subtotal or 0.0
                                    for x in rec.invoice_line])
                amount = rec.amount_total - clear_amount
                rec.diff_expense_amount_flag = \
                    float_compare(amount, rec.amount_expense_request,
                                  precision_digits=1)

    # Move checking to validate
    # @api.one
    # @api.constrains('amount_total')
    # def _check_amount_not_over_expense(self):
    #     # For expense related invoice
    #     # Positive line amount must not over total expense
    #     if self.expense_id:
    #         # Negative amount is advance clearing
    #         clear_amount = sum([x.price_subtotal < 0.0 and
    #                             x.price_subtotal or 0.0
    #                             for x in self.invoice_line])
    #         amount = self.amount_total - clear_amount
    #         # 1 digit precision only to avoid error.
    #         if float_compare(amount, self.expense_id.amount,
    #                          precision_digits=1) == 1:
    #             raise UserError(_('New amount over expense is not allowed!'))

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

    @api.multi
    def action_cancel(self):
        for invoice in self:
            if invoice.expense_id:
                expense = invoice.expense_id
                if expense.state == 'paid':
                    expense.signal_workflow('invoice_except')
                elif expense.state == 'done':
                    expense.signal_workflow('done_to_except')
        return super(AccountInvoice, self).action_cancel()

    @api.multi
    def action_move_create(self):
        result = super(AccountInvoice, self).action_move_create()
        for invoice in self:
            if invoice.diff_expense_amount_flag == 1:
                raise UserError(
                    _('New amount over expense is not allowed!'))
            if invoice.diff_expense_amount_flag == -1 and \
                    not invoice.diff_expense_amount_reason:
                raise UserError(
                    _('Total amount is changed from Expense Request Amount.\n'
                      'Please provide Amount Diff Reason'))
        return result
