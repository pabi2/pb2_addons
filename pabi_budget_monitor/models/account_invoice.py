# -*- coding: utf-8 -*-
from openerp import api, models
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_cancel(self):
        self = self.with_context(force_no_budget_check=True)
        return super(AccountInvoice, self).action_cancel()

    @api.multi
    def _supplier_invoice_budget_check(self):
        Budget = self.env['account.budget']
        for invoice in self:
            if invoice.type == 'in_invoice':  # Check only Supplier Invoice
                doc_date = invoice.date_invoice
                doc_lines = Budget.\
                    convert_lines_to_doc_lines(invoice.invoice_line)
                res = Budget.post_commit_budget_check(doc_date, doc_lines)
                if not res['budget_ok']:
                    raise ValidationError(res['message'])
        return True

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        self._supplier_invoice_budget_check()
        return res
