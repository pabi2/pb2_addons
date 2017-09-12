# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def test_generate_pos_order(self):
        data_dict = {
            'partner_id': u'Yot  Boontongkong',  # Any walking customer
            'user_id': u'Administrator',  # Salesperson
            'workflow_process_id': u'POS',  # workflow_process_id
            'client_order_ref': u'Any reference text',
            'order_line': [
                {
                    'product_id': u'Transfer pipet',
                    'activity_group_id': u'',  # Name of Activity Group
                    'activity_id': u'',  # Name of Activity
                    'name': u'Transfer pipet',  # description
                    'product_uom_qty': 1.0,
                    'product_uom': u'หลอด',
                    'price_unit': 100.0,
                    'tax_id': u'S7',
                },
                {
                    'product_id': u'Transfer pipet',
                    'activity_group_id': u'',  # Name of Activity Group
                    'activity_id': u'',  # Name of Activity
                    'name': u'Transfer pipet 2',  # description
                    'product_uom_qty': 2.0,
                    'product_uom': u'หลอด',
                    'price_unit': 200.0,
                    'tax_id': u'S7',
                },
            ]
        }
        return self.generate_pos_order(data_dict)

    @api.model
    def _pre_process_pos_order(self, data_dict):
        SaleOrder = self.env['sale.order']
        Partner = self.env['res.partner']
        Process = self.env['sale.workflow.process']
        data_dict['order_type'] = 'sale_order'
        partner = Partner.search([('name', '=', data_dict['partner_id'])])
        # Onchange partner
        res = SaleOrder.onchange_partner_id(partner.id)
        values = res['value']
        data_dict['partner_invoice_id/.id'] = values['partner_invoice_id']
        data_dict['pricelist_id/.id'] = values['pricelist_id']
        data_dict['payment_term/.id'] = values['payment_term']
        # Process info
        wf = Process.search([('name', '=', data_dict['workflow_process_id'])])
        if len(wf) != 1:
            raise ValidationError(_('Workflow Process ID mismatch!'))
        data_dict['picking_policy'] = wf.picking_policy
        data_dict['order_policy'] = wf.order_policy
        data_dict['operating_unit_id/.id'] = wf.operating_unit_id.id
        data_dict['warehouse_id/.id'] = wf.warehouse_id.id
        data_dict['taxbranch_id/.id'] = wf.taxbranch_id.id
        section_id = wf.section_id.id
        fund_id = wf.section_id.fund_ids and \
            wf.section_id.fund_ids[0].id or False
        if data_dict.get('order_line', False):
            for order_line in data_dict['order_line']:
                order_line['section_id/.id'] = section_id
                order_line['fund_id/.id'] = fund_id
        return data_dict

    @api.model
    def generate_pos_order(self, data_dict):
        try:
            data_dict = self._pre_process_pos_order(data_dict)
            res = self.env['pabi.utils.ws'].create_data(self._name, data_dict)
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': e,
            }
            self._cr.rollback()
        return res
