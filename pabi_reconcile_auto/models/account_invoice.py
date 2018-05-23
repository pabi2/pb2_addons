# -*- coding: utf-8 -*-
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _reconcile_invoices(self, invoices):
        mlines = invoices.mapped('move_id.line_id')
        mlines.reconcile_special_account()

    @api.multi
    def action_move_create(self):
        res = super(AccountInvoice, self).action_move_create()
        Invoice = self.env['account.invoice']
        for invoice in self:
            # Case HR Expense Advance Clearing, Advance Return
            if invoice.advance_expense_id:
                exp_id = invoice.advance_expense_id.id
                adv_invoices = Invoice.search([('expense_id', '=', exp_id)])
                invoices = invoice | adv_invoices
                mlines = invoices.mapped('move_id.line_id')
                mlines.reconcile_special_account()
            # Case Invoice Plan's advance deposit
            if invoice.source_document_type in ('purchase', 'sale') and \
                    not (invoice.is_advance or invoice.is_deposit):
                order = invoice.source_document_id
                adv_invoices = order.invoice_ids.\
                    filtered(lambda l: l.is_advance or l.is_deposit)
                invoices = invoice | adv_invoices
                mlines = invoices.mapped('move_id.line_id')
                mlines.reconcile_special_account()
        return res
