# -*- coding: utf-8 -*-
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):
        res = super(AccountInvoice, self).action_move_create()
        MoveLine = self.env['account.move.line']
        Auto = self.env['account.auto.reconcile']
        for invoice in self:
            # Case HR Expense: Advance, Clearing, Return
            # Use Advance Numer as auto_reconcile_id
            if invoice.source_document_type in ('expense', 'advance'):
                adv_number = False
                if invoice.supplier_invoice_type == 'expense_advance_invoice':
                    adv_number = invoice.expense_id.number
                elif invoice.advance_expense_id:  # Clearing / Return
                    adv_number = invoice.advance_expense_id.number
                if adv_number:
                    auto_id = Auto.get_auto_reconcile_id(adv_number)
                    invoice.move_id.write({'auto_reconcile_id': auto_id})
                    mlines = MoveLine.search([('auto_reconcile_id',
                                               '=', auto_id)])
                    mlines.reconcile_special_account()
            # All cases, invoice and/or picking is created from PO/So
            # i.e., - Case Invoice Plan's advance deposit
            #       - Case GR/IR, manual or on demand (see stock.py)
            # Use order (po,so) as auto_reconcile_id
            if invoice.source_document_type in ('purchase', 'sale'):
                order_number = invoice.source_document_id.name
                if order_number:
                    auto_id = Auto.get_auto_reconcile_id(order_number)
                    invoice.move_id.write({'auto_reconcile_id': auto_id})
                    mlines = MoveLine.search([
                        ('auto_reconcile_id', '=', auto_id)])
                    print mlines.mapped('move_id')
                    mlines.reconcile_special_account()
                    # x = 1/0
        return res
