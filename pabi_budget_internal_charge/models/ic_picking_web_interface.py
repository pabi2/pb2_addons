# -*- coding: utf-8 -*-import logging
import logging
from openerp import models, api, _
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def test_generate_ic_picking(self):
        data_dict = {
            'partner_id': u'Administrator',
            'picking_type_id': u'เบิกสินค้า ค. สินค้าเบิก Internal Transfers',
            'operating_unit_id': u'สก.',
            'section_id': u'101018',  # Section or Project
            'project_id': False,
            'move_lines': [
                {
                    'name': u'จานรองแก้วดีเอ็นเอ(V)',
                    'product_id': u'จานรองแก้วดีเอ็นเอ(V)',
                    'product_uom_qty': 1,
                    'product_uom': u'Box',
                },
            ]
        }
        return self.generate_ic_picking(data_dict)

    @api.model
    def generate_ic_picking(self, data_dict):
        _logger.info('generate_ic_picking() - input: %s' % data_dict)
        try:
            # Find picking type
            PickType = self.env['stock.picking.type']
            picking_type = PickType.search([
                ('name', '=', data_dict['picking_type_id']),
                ('warehouse_id.operating_unit_id.name', '=',
                 data_dict['operating_unit_id'])])
            if len(picking_type) != 1:
                raise ValidationError(_('No single picking type found!'))
            data_dict['picking_type_id'] = picking_type.id
            # Add source, dest
            src_loc_id = picking_type.default_location_src_id.id
            dest_loc_id = picking_type.default_location_dest_id.id
            for line_dict in data_dict.get('move_lines', []):
                line_dict.update({
                    'invoice_state': 'none',
                    'location_id': src_loc_id,
                    'location_dest_id': dest_loc_id,
                    'picking_type_id': picking_type.id,
                    'section_id': data_dict['section_id'],
                    'project_id': data_dict['project_id'],
                    'product_uos_qty': line_dict['product_uom_qty'],
                    'product_uos': line_dict['product_uom'],
                })
            res = self.env['pabi.utils.ws'].friendly_create_data(self._name,
                                                                 data_dict)
            picking = self.browse(res['result']['id'])
            res['result']['name'] = picking.name
            # Do Transfer
            picking.validate_picking()
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': _(str(e)),
            }
            self._cr.rollback()
        _logger.info('generate_ic_picking() - output: %s' % res)
        return res
