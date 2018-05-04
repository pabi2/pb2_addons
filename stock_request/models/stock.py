# -*- coding: utf-8 -*-
from openerp import models, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'

    for_stock_request = fields.Boolean(
        string='For Stock Request',
        default=True,
    )
    product_ids = fields.Many2many(
        'product.product',
        'location_product_rel',
        'location_id', 'product_id',
        string='Products',
        ondelete='restrict',
    )
