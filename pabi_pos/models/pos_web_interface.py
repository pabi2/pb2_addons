# -*- coding: utf-8 -*-import logging
import logging
from openerp import models, api, _
# from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def test_generate_pos_order(self):
        data_dict = {
            'partner_id': u'Yot  Boontongkong',  # Any walking customer
            'user_id': u'Administrator',  # Salesperson
            'workflow_process_id': u'POS',  # workflow_process_id
            'client_order_ref': u'Any reference text',  # Optional Text
            'origin': u'Tax Document from POS',  # To be preprint num in inv
            'order_line': [
                {
                    'product_id': u'ดินสอดำ',
                    'name': u'ดินสอดำ',  # description
                    'product_uom_qty': 1.0,
                    'product_uom': u'หลอด',
                    'price_unit': 100.0,
                    'tax_id': u'S7',
                },
                {
                    'product_id': u'ดินสอดำ',
                    'name': u'ดินสอดำ',  # description
                    'product_uom_qty': 2.0,
                    'product_uom': u'หลอด',
                    'price_unit': 200.0,
                    'tax_id': u'S7',
                },
            ]
        }
        return self.generate_pos_order(data_dict)

    @api.model
    def generate_pos_order(self, data_dict):
        _logger.info('generate_pos_order() - input: %s' % data_dict)
        try:
            # data_dict = self._pre_process_pos_order(data_dict)
            data_dict['order_type'] = 'sale_order'
            res = self.env['pabi.utils.ws'].friendly_create_data(self._name,
                                                                 data_dict)
            pos = self.browse(res['result']['id'])
            pos.post_process_pos_order()
            # return more data
            res['result']['name'] = pos.name
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': e,
            }
            self._cr.rollback()
        _logger.info('generate_pos_order() - output: %s' % res)
        return res


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
        # Add list_price and uom
        product_ids = [x['product_id'] for x in vals]
        products = self.env['product.product'].browse(product_ids)
        products_dict = dict([(x.id, {'uom_id': x.uom_id.id,
                                      'uom': x.uom_id.name,
                                      'list_price': x.list_price,
                                      'name': x.name,
                                      'default_code': x.default_code, })
                             for x in products])
        for val in vals:
            product = products_dict.get(val['product_id'], {})
            val['uom_id'] = product.get('uom_id', False)
            val['uom'] = product.get('uom', False)
            val['list_price'] = product.get('list_price', False)
            val['name'] = product.get('name', False)
            val['default_code'] = product.get('default_code', False)
        return vals

    @api.model
    def get_pos_product_count(self, pos_name, product_names=None):
        _logger.info('get_pos_product_count() - input: [%s, %s]' %
                     (pos_name, product_names))
        # Always use th_TH
        self = self.with_context(lang='th_TH')
        if product_names is None:
            product_names = []
        WorkflowProcess = self.env['sale.workflow.process']
        pos = WorkflowProcess.search([('name', '=', pos_name)], limit=1)
        warehouse = pos.warehouse_id
        location_id = pos.location_id.id
        if not location_id:
            res = {
                'is_success': False,
                'result': False,
                'messages': _('No location found for POS %s') % pos_name,
            }
            return res
        product_ids = self.search(['|',
                                   ('default_code', 'in', product_names),
                                   ('name', 'in', product_names)]).ids
        result = self._get_product_count_by_loc(location_id, product_ids)
        res = {
            'is_success': True,
            'result': result,
            'messages': _('List of products on warehouse: %s') % warehouse.name
        }
        _logger.info('get_pos_product_count() - output: %s' % res)
        return res


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.model
    def test_create_inventory_adjustment(self):
        data_dict = {
            'name': 'Test Inventory Adjustment',
            'location_id':
                u'Physical Locations / สก. / Stock / ค. หนังสือ-สก.',
            'line_ids': [
                {
                    'product_id': u'ดินสอดำ',
                    'product_uom_id': u'หลอด',
                    'section_id': '100006',
                    'project_id': False,
                    'fund_id': 'NSTDA',
                    'product_qty': 100.00,
                },
                {
                    'product_id': u'ลวดเสียบกระดาษ',
                    'product_uom_id': u'Box',
                    'section_id': '100006',
                    'project_id': False,
                    'fund_id': 'NSTDA',
                    'product_qty': 100.00,
                },
            ]
        }
        return self.create_inventory_adjustment(data_dict)

    @api.model
    def create_inventory_adjustment(self, data_dict):
        _logger.info('create_inventory_adjustment() - input: %s' % data_dict)
        try:
            data_dict['filter'] = 'partial'
            for row in data_dict['line_ids']:
                row['location_id'] = data_dict['location_id']
            res = self.env['pabi.utils.ws'].friendly_create_data(self._name,
                                                                 data_dict)
            adjust = self.browse(res['result']['id'])
            adjust.prepare_inventory()
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': e,
            }
            self._cr.rollback()
        _logger.info('create_inventory_adjustment() - output: %s' % res)
        return res
