# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_date_assign(self):
        self._invoice_check_budget_fund_activity_spending()
        return super(AccountInvoice, self).action_date_assign()

    @api.multi
    def _invoice_check_budget_fund_activity_spending(self):
        FundRule = self.env['budget.fund.rule']
        for invoice in self:
            budget_date = invoice.date_invoice
            if not budget_date:
                budget_date = fields.Date.context_today(self)
            Fiscal = self.env['account.fiscalyear']
            fiscalyear_id = Fiscal.find(budget_date)
            doc_lines = invoice.invoice_line
            FundRule.document_check_fund_activity_spending(fiscalyear_id,
                                                           doc_lines,
                                                           'price_subtotal')
