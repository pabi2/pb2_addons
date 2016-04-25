# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
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
                raise UserError(
                    _("Unit of Measure is missing in some PO line."))
            items.append([0, 0, self._prepare_item(line)])
        res['acceptance_line'] = items
        return res

    @api.model
    def _prepare_acceptance(self):
        lines = []
        vals = {}
        PWAcceptance = self.env['purchase.work.acceptance']
        vals['name'] = self.name
        acceptance = PWAcceptance.create(vals)
        for act_line in self.acceptance_line:
            line_vals = {
                'name': act_line.name,
                'product_id': act_line.product_id.id or False,
                'balance_qty': act_line.balance_qty,
                'to_receive_qty': act_line.to_receive_qty,
                'product_uom': act_line.product_uom.id,
            }
            lines.append([0, 0, line_vals])
        acceptance.acceptance_line = lines
        return acceptance

    @api.multi
    def action_print(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        active_ids = self._context.get('active_ids')
        if active_ids is None:
            return act_close
        assert len(active_ids) == 1, "Only 1 Purchase Order expected"
        acceptance = self._prepare_acceptance()
        acceptance.order_id = active_ids[0]
        return act_close


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
        readonly=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        readonly=True,
    )
    name = fields.Char(
        string='Description',
        required=True,
        readonly=True,
    )
    balance_qty = fields.Float(
        string='Balance Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        required=True,
    )
    to_receive_qty = fields.Float(
        string='To Receive Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        required=True,
    )
    product_uom = fields.Many2one(
        'product.uom',
        string='UoM',
    )
