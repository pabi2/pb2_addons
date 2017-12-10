# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    expense_id = fields.Many2one(
        'hr.expense.expense',
        string="Expense Ref",
        copy=False,
    )

    @api.multi
    def confirm_paid(self):
        result = super(AccountInvoice, self).confirm_paid()
        for invoice in self:
            if invoice.expense_id:
                expense = invoice.expense_id
                invoices = expense.invoice_ids
                if invoices:
                    total_amount = sum([x.amount_total for x in invoices
                                        if x.state == 'paid'])
                    if total_amount == expense.amount:
                        expense.signal_workflow('paid')
                    else:
                        if expense.is_advance_clearing\
                                and invoice.state == 'paid':
                            expense.signal_workflow('paid')
                        else:
                            # Paid, any paid and canel
                            unpaid_invoices = invoices.\
                                filtered(lambda l: l.state
                                         not in ('paid', 'cancel'))
                            if not unpaid_invoices:
                                expense.signal_workflow('paid')
        return result

    @api.multi
    def action_cancel(self):
        result = super(AccountInvoice, self).action_cancel()
        for invoice in self:
            if invoice.expense_id:
                expense = invoice.expense_id
                if expense.state == 'paid':
                    expense.signal_workflow('paid_to_accept')
                if expense.state == 'done':
                    expense.signal_workflow('done_to_accept')
                expense.write({'invoice_id': False})
        return result

    @api.model
    def _get_invoice_total(self, invoice):
        return invoice.amount_total


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    expense_line_ids = fields.Many2many(
        'hr.expense.line',
        'expense_line_invoice_line_rel',
        'invoice_line_id',
        'expense_line_id',
        readonly=True,
        copy=False,
    )
