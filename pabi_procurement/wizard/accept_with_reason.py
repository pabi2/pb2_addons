# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseRequestAcceptReason(models.TransientModel):
    _name = 'purchase.request.accept.reason'

    accept_reason_txt = fields.Char(
        string="Reason",
        readonly=False)

    @api.multi
    def action_accept_with_reason(self):
        self.ensure_one
        act_close = {'type': 'ir.actions.act_window_close'}
        request_id = self._context.get('active_id')
        if request_id is None:
            return act_close
        purchase_request = self.env['purchase.request'].browse(request_id)
        purchase_request.accept_reason_txt = self.accept_reason_txt
        purchase_request.button_approved()
        return act_close
