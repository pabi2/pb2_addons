# -*- coding: utf-8 -*-
from openerp import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    price_subtotal = fields.Float(
        string='Total Cost',
        compute='_compute_price_subtotal',
    )

    @api.multi
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.product_qty
