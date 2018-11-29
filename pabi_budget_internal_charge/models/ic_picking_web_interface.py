# -*- coding: utf-8 -*-import logging
import logging
from openerp import models, api, _

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

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
        return self.generate_ic_picking(data_dict)

    @api.model
    def generate_ic_picking(self, data_dict):
        _logger.info('generate_ic_picking() - input: %s' % data_dict)
        try:
            # data_dict = self._pre_process_pos_order(data_dict)
            data_dict['order_type'] = 'sale_order'
            res = self.env['pabi.utils.ws'].friendly_create_data(self._name,
                                                                 data_dict)
            picking = self.browse(res['result']['id'])
            # pos.post_process_pos_order()
            # auto confirm oder, with async process
            # pos.with_context(pos_async_process=False).action_button_confirm()
            # return more data
            res['result']['name'] = picking.name
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': _(str(e)),
            }
            self._cr.rollback()
        _logger.info('generate_ic_picking() - output: %s' % res)
        return res
