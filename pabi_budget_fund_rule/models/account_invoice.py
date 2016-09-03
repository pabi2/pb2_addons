# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_date_assign(self):
        res = super(AccountInvoice, self).action_date_assign()
        self._invoice_check_budget_fund_activity_spending()
        return res

    @api.multi
    def _invoice_check_budget_fund_activity_spending(self):
        FundRule = self.env['budget.fund.rule']
        Fiscal = self.env['account.fiscalyear']
        for invoice in self:
            if invoice.type != 'in_invoice':
                continue
            fiscalyear_id = Fiscal.find(invoice.date_invoice)
            doc_lines = invoice.invoice_line
            FundRule.document_check_fund_activity_spending(fiscalyear_id,
                                                           doc_lines,
                                                           'price_subtotal')
