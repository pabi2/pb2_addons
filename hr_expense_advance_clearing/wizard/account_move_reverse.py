# -*- coding: utf-8 -*-
from openerp import models, api


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reverse"
    _description = "Create reversal of account moves"

    @api.multi
    def action_reverse_invoice(self):
        res = super(AccountMoveReversal, self).action_reverse_invoice()
        assert 'active_ids' in self.env.context, "active_ids \
                                        missing in context"
        invoice_ids = self.env.context['active_ids']
        invoices = self.env['account.invoice'].browse(invoice_ids)
        for invoice in invoices:
            # first call super call if invoice is clearing then it is
            # not able to cancel invoice from paid state
            # so we made new transition for paid invoice to cancel invoice
            if invoice.is_advance_clearing:
                invoice.signal_workflow('clearing_invoice_cancel')
        return res
