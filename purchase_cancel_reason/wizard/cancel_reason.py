# -*- coding: utf-8 -*-

from openerp import models, fields, api


class PurchaseOrderCancel(models.TransientModel):

    _name = 'purchase.order.cancel'

    cancel_reason_txt = fields.Char(
        string="Reason",
        readonly=False,
        size=500,
    )

    @api.one
    def confirm_cancel(self):

        act_close = {'type': 'ir.actions.act_window_close'}
        order_ids = self._context.get('active_ids')
        if order_ids is None:
            return act_close
        assert len(order_ids) == 1, "Only 1 purchase order expected"
        order = self.env['purchase.order'].browse(order_ids)
        order.cancel_reason_txt = self.cancel_reason_txt
        order.action_cancel()
        # Just to ensure it is cancelled, this may not need
        # self._cr.execute("""
        #     update purchase_order set state = 'cancel' where id = %s
        # """, (order.id, ))
        return act_close
