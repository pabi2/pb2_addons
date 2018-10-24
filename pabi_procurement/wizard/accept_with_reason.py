# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class PurchaseRequestAcceptReason(models.TransientModel):
    _name = 'purchase.request.accept.reason'

    accept_reason_txt = fields.Char(
        string="Reason",
        size=500,
        readonly=False,
    )

    @api.multi
    def action_accept_with_reason(self):
        self.ensure_one
        act_close = {'type': 'ir.actions.act_window_close'}
        request_id = self._context.get('active_id')
        if request_id is None:
            return act_close
        purchase_request = self.env['purchase.request'].browse(request_id)
        if not purchase_request.purchase_method_id:
            raise ValidationError(_('Please specify the purchase method.'))
        purchase_request.accept_reason_txt = self.accept_reason_txt
        purchase_request.button_approved()
        return act_close
