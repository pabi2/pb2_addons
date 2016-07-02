# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

""" This class is intended for Web Service call to/from Alfresco """


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.model
    def test_generate_hr_expense(self):
        data_dict = {
            'name': u'ABCDE',
            'employee_code': u'000039',
            'line_ids': (
                {
                    'activity_id.id': u'4',
                    'name': u'Descripiton 1',
                    'unit_amount': u'1000',
                 },
                {
                    'activity_id.id': u'4',
                    'name': u'Descripiton 2',
                    'unit_amount': u'2000',
                 },
            ),
            'attendee_employee_ids': (
                {
                    'employee_id.id': u'1',
                 },
                {
                    'employee_id.id': u'1',
                 },
                {
                    'employee_id.id': u'1',
                 },
                {
                    'employee_id.id': u'1',
                 },
            )
        }
        return self.generate_hr_expense(data_dict)

    @api.model
    def _pre_process_hr_expense(self, data_dict):
        Expense = self.env['hr.employee']
        # Change employee code to employee_id.id
        domain = [('employee_code', '=', data_dict.get('employee_code'))]
        data_dict['employee_id.id'] = Expense.search(domain).id
        del data_dict['employee_code']
        return data_dict

    @api.model
    def _post_process_hr_expense(self, res):
        return res

    @api.model
    def generate_hr_expense(self, data_dict):
        self._pre_process_hr_expense(data_dict)
        res = self._create_hr_expense_expense(data_dict)
        self._post_process_hr_expense(res)
        return res

    @api.model
    def _finalize_data_to_load(self, fields, data):
        line_count = 1
        # Tables
        _table_fields = ['line_ids', 'attendee_employee_ids']
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
            fields += data_array[table+'_fields']
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
                record += data_array[table+'_data'].values()
            if i == 0:
                datas += [tuple(data + record)]
            else:
                datas += [tuple([False for _x in data] + record)]
        return fields, datas

    @api.model
    def _create_hr_expense_expense(self, data_dict):
        ret = {}
        fields = data_dict.keys()
        data = data_dict.values()
        # Final Preparation of fields and data
        try:
            fields, data = self._finalize_data_to_load(fields, data)
            load_res = self.load(fields, data)
            res_id = load_res['ids'] and load_res['ids'][0] or False
            if not res_id:
                ret = {
                    'is_success': False,
                    'result': False,
                    'messages': [m['message'] for m in load_res['messages']],
                }
            else:
                ret = {
                    'is_success': True,
                    'result': {
                        'id': res_id,
                    },
                    'messages': _('Document created successfully'),
                }
            self._cr.commit()
        except Exception, e:
            ret = {
                'is_success': False,
                'result': False,
                'messages': e,
            }
            self._cr.rollback()
        return ret
