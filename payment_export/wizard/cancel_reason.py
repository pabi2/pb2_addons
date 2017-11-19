# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PaymentExportCancel(models.TransientModel):

    """ Ask a reason for the payment export cancellation."""
    _name = 'payment.export.cancel'
    _description = __doc__

    cancel_reason_txt = fields.Char(
        string="Reason",
        readonly=False)

    @api.one
    def confirm_cancel(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        export_ids = self._context.get('active_ids')
        void_cheque = self._context.get('void_cheque', False)
        if export_ids is None:
            return act_close
        assert len(export_ids) == 1, "Only 1 export ID expected"
        export = self.env['payment.export'].browse(export_ids)
        export.cancel_reason_txt = self.cancel_reason_txt
        export.action_cancel(void_cheque=void_cheque)
        return act_close
