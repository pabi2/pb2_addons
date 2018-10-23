# -*- coding: utf-8 -*-

from openerp import models, fields, api


class PurchaseOrderForceDone(models.TransientModel):

    _name = 'purchase.order.force.done'

    force_done_reason = fields.Char(
        string="Force Done Reason",
        required=True,
        size=500,
    )

    @api.one
    def confirm_force_done(self):
        Picking = self.env['stock.picking']
        act_close = {'type': 'ir.actions.act_window_close'}
        order_ids = self._context.get('active_ids')
        if order_ids is None:
            return act_close
        assert len(order_ids) == 1, "Only 1 purchase order expected"
        orders = self.env['purchase.order'].browse(order_ids)
        for order in orders:
            picking = Picking.search([
                ('state', 'not in', ('done', 'cancel')),
                '|',
                ('origin', '=', order.name),
                ('group_id', '=', order.name),
            ])
            if len(picking) > 0:
                picking.action_cancel()
            order.write({
                'force_done_reason': self.force_done_reason,
            })
            order.wkf_po_done()
            ctx = {'force_release_budget': True}
            order.with_context(ctx).release_all_committed_budget()
        return act_close
