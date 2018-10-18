# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare


class AccountInvoiceRefund(models.TransientModel):

    _inherit = "account.invoice.refund"

    @api.multi
    def invoice_refund(self):
        invoice = self.env['account.invoice'].browse(
            self._context.get('active_id', False)
            )
        if invoice and float_compare(invoice.refunded_amount,
                                     invoice.amount_untaxed, 2) >= 0:
            raise ValidationError(
                _('This will make refund amount exceeded the invoice amount!')
                )
        return super(AccountInvoiceRefund, self).invoice_refund()
