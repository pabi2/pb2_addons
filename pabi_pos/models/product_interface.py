# -*- coding: utf-8 -*-
from openerp import models, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def test_get_pos_product_count(self):
        """ If product names or default_code not specified,
        it will retrieve all products in this POS machine """
        res = self.get_pos_product_count('POS', product_names=[])
        return res

    @api.model
    def _get_product_count_by_loc(self, location_id, product_ids=None):
        if product_ids is None:
            product_ids = []
        """ return dict of product count by location,
        i.e., [{'product_id': 5378, 'product_qty': -24.0}, {'...'}] """
        domain = ' location_id = %s'
        args = (location_id, )
        if product_ids:
            domain += ' and product_id in %s'
            args += (tuple(product_ids),)

        self._cr.execute("""
           SELECT product_id, sum(qty) as product_qty
           FROM stock_quant WHERE""" + domain + """
           GROUP BY product_id
        """, args)

        vals = self._cr.dictfetchall()
        return vals

    @api.model
    def get_pos_product_count(self, pos_name, product_names=None):
        if product_names is None:
            product_names = []
        WorkflowProcess = self.env['sale.workflow.process']
        pos = WorkflowProcess.search([('name', '=', pos_name)], limit=1)
        warehouse = pos.warehouse_id
        location_id = warehouse.lot_stock_id.id
        if not location_id:
            res = {
                'is_success': False,
                'result': False,
                'messages': _('No location found for POS %s') % (pos_name, ),
            }
            return res
        product_ids = self.search(['|',
                                   ('default_code', 'in', product_names),
                                   ('name', 'in', product_names)]).ids
        result = self._get_product_count_by_loc(location_id, product_ids)
        for x in result:
            product = self.browse(x['product_id'])
            x['name'] = product.name
            x['default_code'] = product.default_code
        res = {
            'is_success': True,
            'result': result,
            'messages': _('List of products on warehouse: %s') % warehouse.name
        }
        return res
