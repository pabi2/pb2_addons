# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class AccountVoucherCancel(models.TransientModel):

    """ Ask a reason for the account payment cancellation."""
    _name = 'account.voucher.cancel'
    _description = __doc__

    cancel_reason_txt = fields.Char(
        string="Reason",
        readonly=False,
        size=500,
    )

    @api.multi
    def confirm_cancel(self):
        self.ensure_one()
        act_close = {'type': 'ir.actions.act_window_close'}
        voucher_ids = self._context.get('active_ids')
        if voucher_ids is None:
            return act_close
        assert len(voucher_ids) == 1, "Only 1 sale ID expected"
        voucher = self.env['account.voucher'].browse(voucher_ids)
        if voucher and voucher.bank_receipt_id.state != 'cancel':
            raise ValidationError(_(
                "Bank Receipt %s is not cancelled" %
                (voucher.bank_receipt_id.name)))
        voucher.cancel_reason_txt = self.cancel_reason_txt
        voucher.cancel_voucher()
        return act_close
