# -*- coding: utf-8 -*-
from openerp import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    location_ids = fields.Many2many(
        'stock.location',
        'location_product_rel',
        'product_id', 'location_id',
        string='Locations',
        ondelete='restrict',
    )
