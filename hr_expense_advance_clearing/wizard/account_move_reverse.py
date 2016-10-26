# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import Warning as UserError


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reverse"
    _description = "Create reversal of account moves"

    @api.multi
    def action_reverse_invoice(self):
        assert 'active_ids' in self.env.context, "active_ids \
                                        missing in context"
        invoice_ids = self.env.context['active_ids']
        invoices = self.env['account.invoice'].browse(invoice_ids)
        for invoice in invoices:
            if invoice.invoice_type == 'expense_advance_invoice':
                if invoice.expense_id.advance_clearing_ids:
                    raise UserError(_('Sorry!, \
                        You can not cancel employee advance \
                        invoice since it has already\
                        clearing advance invoices.'))
        res = super(AccountMoveReversal, self).action_reverse_invoice()
        for invoice in invoices:
            # first call super call if invoice is clearing then it is
            # not able to cancel invoice from paid state
            # so we made new transition for paid invoice to cancel invoice
            # if invoice.is_advance_clearing:
            if invoice.invoice_type in ('advance_clearing_invoice',
                                        'expense_advance_invoice'):
                invoice.signal_workflow('clearing_invoice_cancel')
        return res
