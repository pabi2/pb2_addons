# -*- coding: utf-8 -*-

from openerp import models, fields, api, _, exceptions
import openerp.addons.decimal_precision as dp


class PrintPurchaseWorkAcceptance(models.TransientModel):

    _name = 'print.purchase.work.acceptance'

    name = fields.Char(
        string="Acceptance No.",
    )
    acceptance_line = fields.One2many(
        'print.purchase.work.acceptance.item',
        'wiz_id',
        string='Acceptance Lines',
    )

    @api.model
    def _prepare_item(self, line):
        return {
            'line_id': line.id,
            'product_id': line.product_id.id,
            'name': line.name or line.product_id.name,
            'balance_qty': line.product_qty - line.received_qty,
            'to_receive_qty': 0.0,
            'product_uom': line.product_uom.id,
        }

    @api.model
    def default_get(self, fields):
        res = {}
        OrderLine = self.env['purchase.order.line']
        order_ids = self.env.context['active_ids'] or []

        assert len(order_ids) == 1, \
            'Only one order should be printed.'

        items = []

        order_lines = OrderLine.search([('order_id', 'in', order_ids)])
        for line in order_lines:
            if not hasattr(line, 'product_uom'):
                raise exceptions.Warning(
                    _("Unit of Measure is missing in some PO line."))
            items.append([0, 0, self._prepare_item(line)])
        res['acceptance_line'] = items
        return res

    def action_print(self):
        True


class PrintPurchaseWorkAcceptanceItem(models.TransientModel):

    _name = 'print.purchase.work.acceptance.item'

    wiz_id = fields.Many2one(
        'print.purchase.work.acceptance',
        string='Acceptance Reference',
        ondelete='cascade',
    )
    line_id = fields.Many2one(
        'purchase.order.line',
        string='Purchase Order Line',
        required=True,
        readonly=True)
    name = fields.Char(
        string='Description',
        required=True,
    )
    balance_qty = fields.Float(
        string='Balance Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        required=True,
    )
    to_receive_qty = fields.Float(
        string='To Receive Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        required=True
    )
    product_uom = fields.Many2one('product.uom', string='UoM')
