# -*- coding: utf-8 -*-
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):
        res = super(AccountInvoice, self).action_move_create()
        Invoice = self.env['account.invoice']
        for invoice in self:
            # Case HR Expense Advance Clearing
            if invoice.supplier_invoice_type == 'advance_clearing_invoice':
                exp_id = invoice.advance_expense_id and \
                    invoice.advance_expense_id.id
                adv_invoices = Invoice.search([('expense_id', '=', exp_id)])
                cl_mlines = invoice.mapped('move_id.line_id')
                av_mlines = adv_invoices.mapped('move_id.line_id')
                mlines = cl_mlines | av_mlines
                mlines.reconcile_special_account()
        return res
