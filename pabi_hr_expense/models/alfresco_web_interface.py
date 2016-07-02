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
        line_ids = False
        attendee_employee_ids = False
        line_count = 1
        # Tables
        if 'line_ids' in fields:
            i = fields.index('line_ids')
            line_ids = data[i] or ()  # ({'x': 1, 'y': 2}, {})
            del fields[i]
            del data[i]
            line_count = max(line_count, len(line_ids))
        if 'attendee_employee_ids' in fields:
            i = fields.index('attendee_employee_ids')
            attendee_employee_ids = data[i] or ()  # ({'x': 1, 'y': 2}, {})
            del fields[i]
            del data[i]
            line_count = max(line_count, len(attendee_employee_ids))
        # Fields
        line_ids_fields = []
        attendee_employee_ids_fields = []
        if line_ids:
            line_ids_fields = ['line_ids/'+key
                               for key in line_ids[0].keys()]
        if attendee_employee_ids:
            attendee_employee_ids_fields = \
                ['attendee_employee_ids/'+key
                 for key in attendee_employee_ids[0].keys()]
        fields = fields + line_ids_fields + attendee_employee_ids_fields
        print fields
        # Data
        datas = []
        for i in range(0, line_count, 1):
            line = {}
            attendee = {}
            if line_ids_fields:
                line = len(line_ids) > i and line_ids[i] or \
                    {key: False for key in line_ids_fields}
            if attendee_employee_ids_fields:
                attendee = len(attendee_employee_ids) > i and attendee_employee_ids[i] or \
                    {key: False for key in attendee_employee_ids_fields}
            if i == 0:
                datas += [tuple(data + line.values() + attendee.values())]
            else:
                datas += [tuple([False for _x in data] + line.values() + attendee.values())]
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
