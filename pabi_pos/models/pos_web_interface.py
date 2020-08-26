# -*- coding: utf-8 -*-import logging
import logging
from openerp import models, api, _

_logger = logging.getLogger(__name__)


class SalesOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.model
    def _check_current_stock(self, data_dict):
        WorkFlow = self.env['sale.workflow.process']
        try:
            res = {'is_success': True}
            product_dict = {}
            stock_err = {}
            product_err = []
            products = [x['product_id'] for x in data_dict['order_line']]
            for rec in data_dict['order_line']:
                product_dict[rec['product_id']] = rec['product_uom_qty']
            
            workflow = WorkFlow.search([('name', '=', data_dict['workflow_process_id'])])
            if not workflow:
                res = {
                    'is_success': False,
                    'result': False,
                    'messages': _('Not found workflow %s' % data_dict['workflow_process_id']),
                }
            else:
                curr_stock = workflow.location_id.get_current_stock(products)
                for prod in products:
                    if prod not in curr_stock.keys():
                        product_err.append(prod)
                    elif curr_stock[prod] < product_dict[prod]:
                        stock_err[prod] = curr_stock[prod]

            if len(stock_err) > 0 or len(product_err) > 0:
                res = {
                    'is_success': False,
                    'result': {'location': workflow.location_id.name,
                               'stock_line': stock_err,
                               'product_name': product_err},
                    'messages': _('Stock Error!!'),
                }
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': _(str(e)),
            }
        return res

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
                    'discount': 10.0,
                },
                {
                    'product_id': u'ดินสอดำ',
                    'name': u'ดินสอดำ',  # description
                    'product_uom_qty': 2.0,
                    'product_uom': u'หลอด',
                    'price_unit': 200.0,
                    'tax_id': u'S7',
                    'discount': 0.0,
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
            check_stock = self._check_current_stock(data_dict)
            if check_stock['is_success'] == False:
                res = check_stock
            else:
                res = self.env['pabi.utils.ws'].friendly_create_data(self._name,
                                                                     data_dict)
                pos = self.browse(res['result']['id'])
                pos._get_pos_receipt()
                pos.post_process_pos_order()
                # auto confirm oder, with async process
                pos.with_context(pos_async_process=False).action_button_confirm()
                # return more data
                res['result']['name'] = pos.name
                res['result']['origin'] = pos.origin
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': _(str(e)),
            }
            self._cr.rollback()
        _logger.info('generate_pos_order() - output: %s' % res)
        return res

    @api.model
    def cancel_pos_order(self, data_dict):
        _logger.info('cancel_pos_order() - input: %s' % data_dict)
        Voucher = self.env['account.voucher']
        inv_ids = []
        try:
            pos = self.search([('name', '=', data_dict['name'])])
            cancel_id = self.env['res.partner'].search([('name','=',data_dict['cancel_id'])])
            """if not cancel_id:
                return {
                    'is_success': False,
                    'result': False,
                    'messages': _("('ValidateError','%s found no match.')"%(data_dict['cancel_id'])),
                }"""
            pos.cancel_id = cancel_id.id
            pos.cancel_date = data_dict['cancel_date']
            pos.cancel_reason = data_dict['cancel_reason']
            if pos.state == 'done':
                for invoice in pos.invoice_ids:
                    move_ids = invoice.payment_ids.mapped('move_id')._ids
                    voucher_ids = Voucher.search([('move_id', 'in', move_ids)])
                    for voucher in voucher_ids:
                        voucher.cancel_reason_txt = data_dict['cancel_reason']
                        voucher.cancel_voucher()
                    invoice.cancel_reason_txt = data_dict['cancel_reason']
                    invoice.signal_workflow('invoice_cancel')
                for picking in pos.picking_ids:
                    picking.action_picking_cancel()

            if pos.state in ('progress','manual'):
                pos.action_cancel()
            res = {
                'is_success': True,
                'result': pos.name,
                'messages': _('Record cancelled successfully'),
            }
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': _(str(e)),
            }
            self._cr.rollback()
        _logger.info('cancel_pos_order() - output: %s' % res)
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
    def _get_product_count_by_loc(self, location_id, product_names=None):
        if product_names is None:
            product_names = []
        """ return dict of product count by location,
        i.e., [{'product_id': 5378, 'product_qty': -24.0}, {'...'}] """
        if product_names:
            product_ids = self.search(['|',
                                       ('default_code', 'in', product_names),
                                       ('name', 'in', product_names)]).ids
            if not product_ids:
                product_ids = [0]  # No product found
            self._cr.execute("""
               SELECT product_id, sum(qty) as product_qty
               FROM stock_quant WHERE location_id = %s and product_id in %s
               GROUP BY product_id
            """, (location_id, tuple(product_ids)))
        else:
            self._cr.execute("""
                SELECT sq.product_id, sum(sq.qty) as product_qty
                FROM stock_quant sq
                    LEFT JOIN product_product pp on pp.id = sq.product_id
                WHERE pp.active = True and sq.location_id = %s
                GROUP BY sq.product_id
            """, (location_id, ))
        vals = self._cr.dictfetchall()
        # Add list_price and uom
        product_ids = [x['product_id'] for x in vals]
        products = self.env['product.product'].browse(product_ids)
        products_dict = dict([(x.id, {'uom_id': x.uom_id.id,
                                      'uom': x.uom_id.name,
                                      'list_price': x.list_price,
                                      'name': x.name,
                                      'default_code': x.default_code,
                                      'barcode': x.ean13, })
                             for x in products])
        for val in vals:
            product = products_dict.get(val['product_id'], {})
            val['uom_id'] = product.get('uom_id', False)
            val['uom'] = product.get('uom', False)
            val['list_price'] = product.get('list_price', False)
            val['name'] = product.get('name', False)
            val['default_code'] = product.get('default_code', False)
            val['barcode'] = product.get('barcode', False)
        return vals

    @api.model
    def get_pos_product_count(self, pos_name, product_names=None):
        _logger.info('get_pos_product_count() - input: [%s, %s]' %
                     (pos_name, product_names))
        # Always use th_TH
        self = self.with_context(lang='th_TH')
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
        result = self._get_product_count_by_loc(location_id, product_names)
        res = {
            'is_success': True,
            'result': result,
            'messages': _('List of products on warehouse: %s') % warehouse.name
        }
        _logger.info('get_pos_product_count() - output: %s' % res)
        return res

    @api.model
    def get_location_product_count(self, location_name, product_names=None):
        _logger.info('get_location_product_count() - input: [%s, %s]' %
                     (location_name, product_names))
        # Always use th_TH
        self = self.with_context(lang='th_TH')
        Location = self.env['stock.location']
        location = Location.search([('name', '=', location_name)])
        if len(location) != 1:
            res = {
                'is_success': False,
                'result': False,
                'messages': _('No unique location name %s') % location_name,
            }
            return res
        result = self._get_product_count_by_loc(location.id, product_names)
        res = {
            'is_success': True,
            'result': result,
            'messages': _('List of products on location: %s') % location.name
        }
        _logger.info('get_location_product_count() - output: %s' % res)
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
                'messages': _(str(e)),
            }
            self._cr.rollback()
        _logger.info('create_inventory_adjustment() - output: %s' % res)
        return res
