# -*- coding: utf-8 -*-
from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _invoice_budget_check(self):
        Budget = self.env['account.budget']
        for invoice in self:
            if invoice.type != 'in_invoice':
                continue
            active_id = invoice.id
            # Get budget level type resources
            budget_level_info = Budget.\
                get_fiscal_and_budget_level(invoice.date_invoice)
            fiscal_id = budget_level_info['fiscal_id']
            query = Budget.get_document_query('account_invoice',
                                              'account_invoice_line')
            Budget.document_check_budget(query, budget_level_info,
                                         fiscal_id, active_id)
        return True
