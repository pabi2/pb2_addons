# -*- coding: utf-8 -*-
from openerp import models, api, _


class InterfaceAccountEntry(models.Model):
    _inherit = 'interface.account.entry'

    @api.multi
    def test_generate_interface_account_entry(self):
        data_dict = {
            'name': u'Test Interface Account Entry from web',
            'number': u'/',
            'system_id': u'PABI2',
            'type': u'invoice',
            'journal_id': u'Sales Journal',
            'partner_id': u'Kaushik',
            'line_ids': [
                {
                    'name': u'Credit Line',
                    'tax_id': False,
                    'tax_invoice_number': False,
                    'tax_base_amount': 0.0,
                    # Line Info
                    'debit': 428.0,
                    'credit': 0.0,
                    'account_id': u'ลูกหนี้การค้า',
                    'amount_currency': 400.0,
                    'currency_id': u'THB',
                    'partner_id': u'Kaushik',
                    'operating_unit_id': u'ศว.',
                    'activity_group_id': False,
                    'activity_id': False,
                    'section_id': False,
                    'project_id': False,
                    'taxbranch_id': False,
                    'date': u'2017-01-13',
                    'date_maturity':  u'2017-01-14',
                },
                {
                    'name': u'Debit Line-1',
                    'tax_id': u'Undue Output VAT 7%',
                    'tax_invoice_number': u'IV16001',
                    'tax_base_amount': 400.0,
                    # Line Info
                    'debit': 0.0,
                    'credit': 28.0,
                    'account_id': u'พักภาษีขาย',
                    'amount_currency': 28.0,
                    'currency_id': u'THB',
                    'partner_id': u'Kaushik',
                    'operating_unit_id': u'ศว.',
                    'activity_group_id': False,
                    'activity_id': False,
                    'section_id': False,
                    'project_id': False,
                    'taxbranch_id': u'ศูนย์เทคโนโลยีโลหะและวัสดุแห่งชาติ',
                    'date': u'2017-01-13',
                    'date_maturity':  u'',
                },
                {
                    'name': u'Debit Line-2',
                    'tax_id': False,
                    'tax_invoice_number': u'IV16001',
                    'tax_base_amount': 0.0,
                    # Line Info
                    'debit': 0.0,
                    'credit': 400.0,
                    'account_id': u'วิเคราะห์ทดสอบ/สอบเทียบ/ใบรับรองคุณภาพ',
                    'amount_currency': 400.0,
                    'currency_id': u'THB',
                    'partner_id': u'Kaushik',
                    'operating_unit_id': u'ศว.',
                    'activity_group_id': u'ค่าวิเคราะห์และทดสอบ',
                    'activity_id': u'ให้บริการวิเคราะห์ทดสอบ/ร่วมวิจัย/'
                    u'รับจ้างวิจัย/เครื่องมือวัด/สอบเทียบ/ใบรับรองคุณภาพ',
                    'section_id': u'Procurement Section',
                    'project_id': False,
                    'taxbranch_id': False,
                    'date': u'2017-01-13',
                    'date_maturity':  u'',
                }
            ]
        }
        return self.generate_interface_account_entry(data_dict)

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
            data_array[table+'_fields'] = False
            if table in fields:
                i = fields.index(table)
                data_array[table] = data[i] or ()  # ({'x': 1, 'y': 2}, {})
                del fields[i]
                del data[i]
                line_count = max(line_count, len(data_array[table]))
            if data_array[table]:
                data_array[table+'_fields'] = \
                    [table+'/'+key for key in data_array[table][0].keys()]
            fields += data_array[table+'_fields'] or []
        # Data
        datas = []
        for i in range(0, line_count, 1):
            record = []
            for table in _table_fields:
                data_array[table+'_data'] = False
                if data_array[table+'_fields']:
                    data_array[table+'_data'] = \
                        (len(data_array[table]) > i and data_array[table][i] or
                         {key: False for key in data_array[table+'_fields']})
                record += data_array[table+'_data'] and \
                    data_array[table+'_data'].values() or []
            if i == 0:
                datas += [tuple(data + record)]
            else:
                datas += [tuple([False for _x in data] + record)]
        return fields, datas

    @api.model
    def _pre_process_interface_account_entry(self, data_dict):
        return data_dict

    @api.model
    def _create_interface_account_entry(self, data_dict):
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
    def generate_interface_account_entry(self, data_dict):
        try:
            data_dict = self._pre_process_interface_account_entry(data_dict)
            res = self._create_interface_account_entry(data_dict)
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': e,
            }
            self._cr.rollback()
        return res
