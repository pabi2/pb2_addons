# -*- coding: utf-8 -*-
from openerp import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _prepare_order_line_move(self, order, order_line,
                                 picking_id, group_id):
        res = super(PurchaseOrder, self).\
            _prepare_order_line_move(order, order_line, picking_id, group_id)
        Product = self.env['product.product']
        asset_loc = self.env.ref('pabi_asset_management.stock_location_assets')
        for r in res:
            if r['product_id']:
                product = Product.browse(r['product_id'])
                if product.asset:
                    r['location_dest_id'] = asset_loc.id
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    parent_asset_id = fields.Many2one(
        'account.asset.asset',
        string='Prototype',
        domain="[('parent_id', '=', False),('type', '=', 'view'),"
        "'|',('project_id', '=', project_id),('section_id', '=', section_id)]",
        help="The project prototype the receiving asset will belong to.",
    )
