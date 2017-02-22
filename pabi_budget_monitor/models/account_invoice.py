# -*- coding: utf-8 -*-
from openerp import api, models
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_date_assign(self):
        res = super(AccountInvoice, self).action_date_assign()
        self._invoice_budget_check()
        return res

    @api.multi
    def _invoice_budget_check(self):
        Budget = self.env['account.budget']
        for invoice in self:
            if invoice.type != 'in_invoice':
                continue
            doc_date = invoice.date_invoice
            doc_lines = Budget.convert_lines_to_doc_lines(invoice.invoice_line)
            res = Budget.document_check_budget(doc_date,
                                               doc_lines,
                                               'price_subtotal')
            if not res['budget_ok']:
                raise UserError(res['message'])
        return True
