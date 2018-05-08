# -*- coding: utf-8 -*-

from openerp import models, fields, api


class PurchaseOrderCancel(models.TransientModel):

    _name = 'purchase.order.cancel'

    cancel_reason_txt = fields.Char(
        string="Reason",
        readonly=False)

    @api.one
    def confirm_cancel(self):

        act_close = {'type': 'ir.actions.act_window_close'}
        order_ids = self._context.get('active_ids')
        if order_ids is None:
            return act_close
        assert len(order_ids) == 1, "Only 1 purchase order expected"
        order = self.env['purchase.order'].browse(order_ids)
        order.cancel_reason_txt = self.cancel_reason_txt
        order.signal_workflow('purchase_cancel')
        order.state = 'cancel'
        return act_close
