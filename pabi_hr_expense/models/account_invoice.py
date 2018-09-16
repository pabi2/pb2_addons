# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
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
    diff_expense_amount_adjusted = fields.Float(
        string='Adjusted Amount',
        compute='_compute_diff_expense_amount_flag',
        readonly=True,
        default=0.0,
        help="New adjusted amount in invoice, comparing to expense amount",
    )
    diff_expense_amount_reason = fields.Char(
        string='Amount Diff Reason',
        readonly=True,
        size=500,
        states={'draft': [('readonly', False)]},
        help="Reason when amount is different from Expense",
    )

    @api.multi
    @api.depends('amount_total')
    def _compute_diff_expense_amount_flag(self):
        for rec in self:
            if rec.expense_id:
                # clear_amount = sum([x.price_subtotal < 0.0 and
                #                     x.price_subtotal or 0.0
                #                     for x in rec.invoice_line])
                # amount = rec.amount_total - clear_amount
                amount = rec.amount_total
                rec.diff_expense_amount_adjusted = amount
                rec.diff_expense_amount_flag = \
                    float_compare(amount, rec.amount_expense_request,
                                  precision_digits=1)

    @api.onchange('advance_expense_id')
    def _onchange_advance_expense_id(self):
        super(AccountInvoice, self)._onchange_advance_expense_id()
        if len(self.taxbranch_ids) == 1:
            self.taxbranch_id = self.taxbranch_ids[0].id

    @api.multi
    def confirm_paid(self):
        expenses = self.env['hr.expense.expense'].search([('invoice_id',
                                                           'in', self._ids)])
        History = self.env['hr.expense.advance.due.history']
        Voucher = self.env['account.voucher']
        for expense in expenses:
            if not expense.is_employee_advance:
                continue
            date_due = False
            # Case 1) buy_product, date_due = date_value + 30 days
            if expense.advance_type == 'buy_product':
                move_ids = \
                    expense.invoice_id.payment_ids.mapped('move_id')._ids
                vouchers = Voucher.search([('move_id', 'in', move_ids)],
                                          order='date desc', limit=1)
                date_paid = vouchers[0].date_value
                date_due = (datetime.strptime(date_paid, '%Y-%m-%d') +
                            relativedelta(days=30))
            # Case 2) attend_seminar, date_due = arrive date + 30 days
            elif expense.advance_type == 'attend_seminar':
                date_back = expense.date_back
                date_due = (datetime.strptime(date_back, '%Y-%m-%d') +
                            relativedelta(days=30))
            else:
                raise ValidationError(_('Can not calculate due date. '
                                        'No Advance Type vs Due Date Rule'))
            if date_due:
                History.create({
                    'expense_id': expense.id,
                    'date_due': date_due.strftime('%Y-%m-%d'),
                })
        return super(AccountInvoice, self).confirm_paid()

    # @api.multi
    # def action_cancel(self):
    #     for invoice in self:
    #         if invoice.expense_id:
    #             expense = invoice.expense_id
    #             if expense.state == 'paid':
    #                 expense.signal_workflow('invoice_except')
    #             elif expense.state == 'done':
    #                 expense.signal_workflow('done_to_except')
    #     return super(AccountInvoice, self).action_cancel()

    @api.multi
    def action_move_create(self):
        result = super(AccountInvoice, self).action_move_create()
        for invoice in self:
            if invoice.diff_expense_amount_flag == 1:
                raise ValidationError(
                    _('New amount over expense is not allowed!'))
            if invoice.diff_expense_amount_flag == -1 and \
                    not invoice.diff_expense_amount_reason:
                raise ValidationError(
                    _('Total amount is changed from Expense Request Amount.\n'
                      'Please provide Amount Diff Reason'))
        return result
