# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    location_ids = fields.Many2many(
        'stock.location',
        'location_product_rel',
        'product_id', 'location_id',
        string='Locations',
        ondelete='restrict',
    )

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # Conditional domain based on type of request
        stock_request_type = self._context.get('stock_request_type', False)
        location_id = self._context.get('location_id', False)
        location_dest_id = self._context.get('location_dest_id', False)
        location_borrow_id = self._context.get('location_borrow_id', False)
        if stock_request_type == 'request':
            args += [('location_ids', 'in', location_id)]
        if stock_request_type == 'transfer':
            args += [('location_ids', 'in', location_id),
                     ('location_ids', 'in', location_dest_id)]
        if stock_request_type == 'borrow':
            args += [('location_ids', 'in', location_id),
                     ('location_ids', 'in', location_borrow_id)]
        return super(ProductProduct, self).search(args, offset=offset,
                                                  limit=limit, order=order,
                                                  count=count)
