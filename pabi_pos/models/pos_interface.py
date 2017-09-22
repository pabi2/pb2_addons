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
    def _pre_process_pos_order(self, data_dict):
        SaleOrder = self.env['sale.order']
        Partner = self.env['res.partner']
        Product = self.env['product.product']
        Process = self.env['sale.workflow.process']
        # Process info
        wf = Process.search([('name', '=', data_dict['workflow_process_id'])],
                            limit=1)
        if len(wf) != 1:
            raise ValidationError(_('Workflow Process ID mismatch!'))
        # Partner
        partner = False
        if not data_dict.get('partner_id'):
            partner = wf.pos_partner_id
        else:
            partner = Partner.search([('name', '=', data_dict['partner_id'])],
                                     limit=1)
        if not partner:
            raise ValidationError(
                _('Partner "%s" not found!') % (data_dict['partner_id'],))
        # Starts
        data_dict['order_type'] = 'sale_order'
        # Onchange partner
        res = SaleOrder.onchange_partner_id(partner.id)
        values = res['value']
        data_dict['partner_invoice_id/.id'] = values['partner_invoice_id']
        data_dict['pricelist_id/.id'] = values['pricelist_id']
        data_dict['payment_term/.id'] = values['payment_term']
        data_dict['picking_policy'] = wf.picking_policy
        data_dict['order_policy'] = wf.order_policy
        data_dict['operating_unit_id/.id'] = wf.operating_unit_id.id
        data_dict['warehouse_id/.id'] = wf.warehouse_id.id
        data_dict['taxbranch_id/.id'] = wf.taxbranch_id.id
        section_id = wf.res_section_id.id
        fund_id = wf.res_section_id.fund_ids and \
            wf.res_section_id.fund_ids[0].id or False
        if data_dict.get('order_line', False):
            for order_line in data_dict['order_line']:
                order_line['section_id/.id'] = section_id
                order_line['fund_id/.id'] = fund_id
                # Match product
                prod = order_line.get('product_id', False)
                product = False
                if not prod:
                    raise ValidationError(_('No product in POS order!'))
                product = Product.search([('default_code', '=', prod)]) or \
                    Product.search([('name', '=', prod)])
                if not product or len(product) != 1:
                    raise ValidationError(
                        _('Product "%s" not found!') % (prod,))
                order_line['product_id/.id'] = product.id
                order_line.pop('product_id')
                # AG/A
                order_line['activity_group_id/.id'] = \
                    product.categ_id.activity_group_id.id
                order_line['activity_rpt_id/.id'] = \
                    product.categ_id.activity_id.id
                if not order_line['activity_group_id/.id'] or \
                        not order_line['activity_rpt_id/.id']:
                    raise ValidationError(
                        _('No AG/A for product %s!') % (prod,))
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
