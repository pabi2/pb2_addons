# -*- coding: utf-8 -*-import logging
import logging
from openerp import models, fields, api, _

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'Test PR'

    @api.model
    def test_generate_ic_picking(self):
        data_dict = {
            'partner_id': u'Administrator',
            'picking_type_id': u'เบิกสินค้า ค. วัสดุ Internal Transfers',
            'operating_unit_id': u'สก.',
            'move_lines': [
                {
                    'product_id': u'คลิปดำ เบอร์108',
                    'product_uom_qty': u'Box',
                    'price_unit': 100.00,
                },
            ]
        }
        return self.generate_ic_picking(data_dict)

    @api.model
    def generate_ic_picking(self, data_dict):
        _logger.info('generate_ic_picking() - input: %s' % data_dict)
        try:
            data_dict['date'] = fields.Datetime.now()
            res = self.env['pabi.utils.ws'].friendly_create_data(self._name,
                                                                 data_dict)
            picking = self.browse(res['result']['id'])
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
