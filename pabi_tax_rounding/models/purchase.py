# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    round_total = fields.Boolean(
        default=False,
    )
    amount_untaxed = fields.Float(
        compute='_amount_all',
        store=True,
    )
    amount_tax = fields.Float(
        compute='_amount_all',
        store=True,
    )
    amount_total = fields.Float(
        compute='_amount_all',
        store=True,
    )

    @api.multi
    @api.depends('round_total', 'order_line.price_subtotal')
    def _amount_all(self):
        line_obj = self.env['purchase.order.line']
        for order in self:
            order.amount_untaxed = 0.0
            order.amount_tax = 0.0
            order.amount_total = 0.0
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                line_price = line_obj._calc_line_base_price(line)
                line_qty = line_obj._calc_line_quantity(line)
                for c in line.taxes_id.compute_all(
                        line_price, line_qty, line.product_id, order.partner_id
                        )['taxes']:
                    val += c.get('amount', 0.0)
            order.amount_tax = cur.round(val)
            order.amount_untaxed = cur.round(val1)
            order.amount_total = order.amount_untaxed + order.amount_tax
            # Tax Rounding
            if order.round_total:
                order.amount_total = round(order.amount_total, 0)
                order.amount_tax = order.amount_total - order.amount_untaxed
        return True
