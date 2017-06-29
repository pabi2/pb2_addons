# -*- coding: utf-8 -*-

from openerp import models, fields, api


class PurchaseRequestReject(models.TransientModel):

    _name = 'purchase.request.reject'

    reject_reason_txt = fields.Char(
        string="Reason",
        readonly=False)

    @api.one
    def confirm_reject(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        request_ids = self._context.get('active_ids')
        if request_ids is None:
            return act_close
        assert len(request_ids) == 1, "Only 1 purchase request expected"
        request = self.env['purchase.request'].browse(request_ids)
        request.reject_reason_txt = self.reject_reason_txt
        request.button_rejected()
        return act_close
