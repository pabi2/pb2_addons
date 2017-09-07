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
    def _finalize_data_to_load(self, data_dict):
        """
        This method will convert user friendly data_dict
        to load() compatible fields/data
        Currently it is working with multiple line table but with 1 level only
        data_dict = {
            'name': 'ABC',
            'line_ids': ({'desc': 'DESC'},),
            'line2_ids': ({'desc': 'DESC'},),
        }
        to
        fields = ['name', 'line_ids/desc', 'line2_ids/desc']
        data = [('ABC', 'DESC', 'DESC')]
        """
        fields = data_dict.keys()
        data = data_dict.values()
        line_count = 1
        _table_fields = []  # Tuple fields
        for key in fields:
            if isinstance(data_dict[key], list) or \
                    isinstance(data_dict[key], tuple):
                _table_fields.append(key)
        data_array = {}
        for table in _table_fields:
            data_array[table] = False
            data_array[table + '_fields'] = False
            if table in fields:
                i = fields.index(table)
                data_array[table] = data[i] or ()  # ({'x': 1, 'y': 2}, {})
                del fields[i]
                del data[i]
                line_count = max(line_count, len(data_array[table]))
            if data_array[table]:
                data_array[table + '_fields'] = \
                    [table + '/' + key for key in data_array[table][0].keys()]
            fields += data_array[table + '_fields'] or []
        # Data
        datas = []
        for i in range(0, line_count, 1):
            record = []
            for table in _table_fields:
                data_array[table + '_data'] = False
                if data_array[table + '_fields']:
                    data_array[table + '_data'] = \
                        (len(data_array[table]) > i and data_array[table][i] or
                         {key: False for key in data_array[table + '_fields']})
                record += data_array[table + '_data'] and \
                    data_array[table + '_data'].values() or []
            if i == 0:
                datas += [tuple(data + record)]
            else:
                datas += [tuple([False for _x in data] + record)]
        return fields, datas

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
    def _create_pos_order(self, data_dict):
        res = {}
        # Final Preparation of fields and data
        fields, data = self._finalize_data_to_load(data_dict)
        load_res = self.load(fields, data)
        res_id = load_res['ids'] and load_res['ids'][0] or False
        if not res_id:
            res = {
                'is_success': False,
                'result': False,
                'messages': [m['message'] for m in load_res['messages']],
            }
        else:
            res = {
                'is_success': True,
                'result': {
                    'id': res_id,
                },
                'messages': _('Document created successfully'),
            }
        return res

    @api.model
    def generate_pos_order(self, data_dict):
        try:
            data_dict = self._pre_process_pos_order(data_dict)
            res = self._create_pos_order(data_dict)
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': e,
            }
            self._cr.rollback()
        return res
