# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountBankReceiptCancel(models.TransientModel):

    """ Ask a reason for the account bank receipt cancellation."""
    _name = 'account.bank.receipt.cancel'
    _description = __doc__

    cancel_reason_txt = fields.Char(
        string="Reason",
        readonly=False
    )

    @api.multi
    def confirm_cancel(self):
        self.ensure_one()
        act_close = {'type': 'ir.actions.act_window_close'}
        bank_receipt_ids = self._context.get('active_ids')
        if bank_receipt_ids is None:
            return act_close
        assert len(bank_receipt_ids) == 1, "Only 1 sale ID expected"
        BankReceipt = self.env['account.bank.receipt']
        bank_receipt = BankReceipt.browse(bank_receipt_ids[0])
        bank_receipt.write({'cancel_reason_txt': self.cancel_reason_txt})
        bank_receipt.cancel_bank_receipt()
        return act_close
