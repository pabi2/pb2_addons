# -*- coding: utf-8 -*-
from openerp import api, models


class AccountInvoiceConfirm(models.TransientModel):
    _inherit = "account.invoice.confirm"

    @api.multi
    def invoice_confirm(self):
        # Check for loan case only, each set of loan invoices
        # Must not make advance installment validation
        active_ids = self._context.get('active_ids', []) or []
        Invoice = self.env['account.invoice']
        invoices = Invoice.browse(active_ids)
        loan_ids = list(set(invoices.mapped('loan_agreement_id.id')))
        if False in loan_ids:
            loan_ids.remove(False)
        for loan_id in loan_ids:
            date_dues = invoices.filtered(
                lambda l: l.loan_agreement_id.id == loan_id).mapped('date_due')
            date_due = min(date_dues)
            Invoice._check_loan_invoice_in_advance(loan_id, date_due)
        # Make sure it won't be check again.
        invoices.write({'discard_installment_order_check': True})
        return super(AccountInvoiceConfirm, self).invoice_confirm()
