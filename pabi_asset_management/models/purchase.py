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

    @api.multi
    def wkf_confirm_order(self):
        """
        On confirm order, check for duplicated asset and change to variants
        """
        res = super(PurchaseOrder, self).wkf_confirm_order()
        self._fix_duplicated_product_asset_to_variant()
        return res

    @api.multi
    def _fix_duplicated_product_asset_to_variant(self):
        """ To ensure that, there will be no line with same product,
        by changing that product to its inactive varient """
        for po in self:
            """ Get duplicate stockable product in PO line """
            self._cr.execute("""
                select product_id, count from
                (select p.id product_id, count(l.product_id)
                from purchase_order_line l
                join purchase_order o on l.order_id = o.id
                join product_product p on p.id = l.product_id
                join product_template pt on pt.id = p.product_tmpl_id
                where o.id = %s
                and pt.asset = true  -- Concern on assets only
                and pt.type != 'service'  -- Focus on stockable only
                group by p.id) a where a.count > 1
            """, (po.id, ))
            res = self._cr.fetchall()
            # For any products with duplication, get the variants
            product_variants = {}  # product_id to variants, i.e., {1: [2, 3]}
            Prod = self.env['product.product'].with_context(active_test=False)
            for (product_id, count) in res:
                product = Prod.browse(product_id)
                variants = product.product_tmpl_id.product_variant_ids
                product_variants[product_id] = variants.ids
                if len(variants) < count:
                    extra = count - len(variants)
                    for i in range(extra):
                        active_variant = variants.filtered('active')
                        new_variant = active_variant[0].copy({
                            'active': False,
                            'product_tmpl_id': product.product_tmpl_id.id,
                        })
                        product_variants[product_id].append(new_variant.id)
            # Change product to its variants
            for line in po.order_line:
                if product_variants.get(line.product_id.id, False):
                    var_product_id = product_variants[line.product_id.id].pop()
                    line.write({'product_id': var_product_id})
        return True


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    parent_asset_id = fields.Many2one(
        'account.asset',
        string='Parent Asset',
        domain="[('parent_id', '=', False),('type', '=', 'view'),"
        "('state', '=', 'draft'),"
        "'|',('project_id', '=', [project_id or -1]),"
        "('section_id', '=', [section_id or -1])]",
        help="The project prototype the receiving asset will belong to.",
    )
