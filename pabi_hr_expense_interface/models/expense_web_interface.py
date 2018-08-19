# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.model
    def test_generate_hr_expense_advance(self):  # For Advance Only
        data_dict = {
            'is_employee_advance': u'True',
            'number': u'/',  # av_id
            'employee_code': u'004012',  # requester
            'preparer_code': u'004012',  # preparer
            'date': u'2016-01-31',  # by_time
            'advance_type': u'attend_seminar',  # attend_seminar, buy_product
            'date_back': u'2016-10-30',  # back from seminar
            'name': u'From Description field',  # objective
            'note': u'From Reason field',
            'apweb_ref_url': u'XXX',
            'receive_method': 'other_bank',  # salary_bank, other_bank
            'employee_bank_id.id': u'64',
            'line_ids': [  # 1 line only, Advance
                {
                    'section_id.id': u'434',
                    'project_id.id': u'',
                    'invest_asset_id.id': u'',
                    'invest_construction_phase_id.id': u'',
                    'fund_id.id': u'1',
                    'is_advance_product_line': u'True',
                    'name': u'Employee Advance',
                    'unit_amount': u'2000',  # total
                    'cost_control_id.id': u'',
                },
                {
                    'section_id.id': u'434',
                    'project_id.id': u'',
                    'invest_asset_id.id': u'',
                    'invest_construction_phase_id.id': u'',
                    'fund_id.id': u'1',
                    'is_advance_product_line': u'True',
                    'name': u'Employee Advance 2',  # Expense Note (not in AF?)
                    'unit_amount': u'3000',  # total
                    'cost_control_id.id': u'',
                },
            ],
            'attendee_employee_ids': [
                {
                    'sequence': u'1',
                    'employee_code': u'000143',
                },
                {
                    'sequence': u'2',
                    'employee_code': u'000165',
                },
            ],
            'attendee_external_ids': [
                {
                    'sequence': u'1',
                    'attendee_name': u'Walai.',
                    'position': u'Manager',
                },
                {
                    'sequence': u'2',
                    'attendee_name': u'Thongchai.',
                    'position': u'Programmer',
                },
            ],
            'attachment_ids': [
                {
                    'name': u'Expense1.pdf',
                    'description': u'My Expense 1 Document Description',
                    'url': u'b1d1d9a9-740f-42ad-a96b-b4747edbae1d',
                },
                {
                    'name': u'Expense2.pdf',
                    'description': u'My Expense 2 Document Description',
                    'url': u'b1d1d9a9-740f-42ad-a96b-b4747edbae1d',
                },
            ]
        }
        return self.generate_hr_expense(data_dict, test=True)

    @api.model
    def test_generate_hr_expense_expense(self):  # Expense / Advance
        # Payment Type
        # ------------
        # 1) Employee
        #  - pay_to = 'employee'
        #  - supplier_text = None
        #  - is_advance_clearing = False
        #  - is_employee_advance = False
        # 2) Supplier
        #  - pay_to = 'supplier'
        #  - supplier_text = 'AAA Co., Ltd.'
        #  - is_advance_clearing = False
        #  - is_employee_advance = False
        # 3) Advance
        #  - pay_to = 'employee'
        #  - supplier_text = False
        #  - is_advance_clearing = True
        #  - is_employee_advance = False
        # 4) Internal Charge
        #  - pay_to = 'internal'
        #  - supplier_text = False
        #  - is_advance_clearing = False
        #  - is_employee_advance = False
        #  - internal_section_id OR internal_project_id (not both)
        # 5) Petty Cash
        #  - pay_to = 'pettycash'
        #  - is_advance_clearing = False
        #  - is_employee_advance = False
        #  - pettycash_id.id = u'1'   (from account.pettycash)
        data_dict = {
            'pay_to': u'supplier',  # 'employee', 'supplier'
            'supplier_text': u'AAA Co., Ltd.',  # If Pay to Supplier
            'is_advance_clearing': u'False',  # True if Clear Advance
            'is_employee_advance': u'False',
            'internal_section_id': u'101012',  # Only for Internal Charge
            'internal_project_id': False,  # Only for Internal Charge
            'number': u'/',  # expense number
            'employee_code': u'004012',
            'preparer_code': u'004012',
            'approver_code': u'004012',
            'date': u'2016-01-31',
            'advance_type': u'attend_seminar',  # attend_seminar, buy_product
            'date_back': u'2016-10-30',  # back from seminar
            'name': u'From Description field',  # objective
            'note': u'From Reason field',
            'apweb_ref_url': u'XXX',
            'receive_method': 'other_bank',  # salary_bank, other_bank
            'employee_bank_id.id': u'64',
            'advance_expense_number': u'',  # Case clearing, refer Exp Advance
            'pettycash_id.id': u'1',  # Case pettycash, from account.pettycash
            'origin_pr_number': u'',  # If small amount, has origin_pr_number
            'line_ids': [  # 1 line only, Advance
                {
                    'section_id.id': u'434',
                    'project_id.id': u'',
                    'invest_asset_id.id': u'',
                    'invest_construction_phase_id.id': u'',
                    'fund_id.id': u'1',
                    'is_advance_product_line': u'False',  # Must be False
                    'activity_group_id.id': u'59',
                    'activity_id.id': u'3',
                    'name': u'Some Expense',
                    'unit_amount': u'2000',  # total
                    'cost_control_id.id': u'',
                },
                {
                    'section_id.id': u'434',
                    'project_id.id': u'',
                    'invest_asset_id.id': u'',
                    'invest_construction_phase_id.id': u'',
                    'fund_id.id': u'1',
                    'is_advance_product_line': u'False',  # Must be False
                    'activity_group_id.id': u'59',
                    'activity_id.id': u'3',
                    'name': u'Some Expense',  # Expense Note (not in AF?)
                    'unit_amount': u'3000',  # total
                    'cost_control_id.id': u'',
                },
            ],
            'attendee_employee_ids': [
                {
                    'sequence': u'1',
                    'employee_code': u'000143',
                },
                {
                    'sequence': u'2',
                    'employee_code': u'000165',
                },
            ],
            'attendee_external_ids': [
                {
                    'sequence': u'1',
                    'attendee_name': u'Walai.',
                    'position': u'Manager',
                },
                {
                    'sequence': u'2',
                    'attendee_name': u'Thongchai.',
                    'position': u'Programmer',
                },
            ],
            'attachment_ids': [
                {
                    'name': u'Expense1.pdf',
                    'description': u'My Expense 1 Document Description',
                    'url': u'b1d1d9a9-740f-42ad-a96b-b4747edbae1d',
                    'attach_by': u'000143',
                },
                {
                    'name': u'Expense2.pdf',
                    'description': u'My Expense 2 Document Description',
                    'url': u'b1d1d9a9-740f-42ad-a96b-b4747edbae1d',
                    'attach_by': u'000143',
                },
            ]
        }
        return self.generate_hr_expense(data_dict, test=True)

    @api.model
    def _pre_process_hr_expense(self, data_dict):
        Employee = self.env['hr.employee']
        # employee_code to employee_id.id
        domain = [('employee_code', '=', data_dict.get('employee_code'))]
        employee = Employee.search(domain)
        data_dict['employee_id.id'] = employee.id or u''
        del data_dict['employee_code']
        # advance expense if any
        if data_dict.get('advance_expense_number', '') != '':
            domain = [('number', '=', data_dict.get('advance_expense_number'))]
            expense = self.search(domain)
            data_dict['advance_expense_id.id'] = expense.id or u''
        if 'advance_expense_number' in data_dict:
            del data_dict['advance_expense_number']
        # Small amount origin_pr_number if any
        if data_dict.get('origin_pr_number', '') != '':
            domain = [('name', '=', data_dict.get('origin_pr_number'))]
            pr = self.search(domain)
            data_dict['origin_pr_id.id'] = pr.id or u''
        if 'origin_pr_number' in data_dict:
            del data_dict['origin_pr_number']
        # preparer_code to user_id.id
        domain = [('employee_code', '=', data_dict.get('preparer_code'))]
        employee = Employee.search(domain)
        data_dict['user_id.id'] = employee.user_id.id or u''
        del data_dict['preparer_code']
        # OU based on employee
        data_dict['operating_unit_id.id'] = \
            employee.org_id.operating_unit_id.id
        # approver_code to approver_id.id
        domain = [('employee_code', '=', data_dict.get('approver_code'))]
        employee = Employee.search(domain)
        data_dict['approver_id.id'] = employee.user_id.id or u''
        del data_dict['approver_code']
        # Advance Case, mrege lines
        if data_dict.get('is_employee_advance', u'False') == u'True' and \
                'line_ids' in data_dict:
            if len(data_dict['line_ids']) > 0:  # >1 lines, merge ignore detail
                i = 0
                merged_line = {}
                for line_dict in data_dict['line_ids']:
                    if i == 0:
                        merged_line = line_dict.copy()
                    else:
                        merged_line['name'] += ', ' + line_dict['name']
                        merged_line['unit_amount'] = \
                            float(merged_line['unit_amount']) + \
                            float(line_dict['unit_amount'])
                    i += 1
                merged_line['activity_group_id.id'] = u''
                merged_line['activity_id.id'] = u''
                data_dict['line_ids'] = [merged_line]
        if 'line_ids' in data_dict:
            for data in data_dict['line_ids']:
                if not data.get('name', False):
                    Activity = self.env['account.activity']
                    activity = Activity.browse(int(data['activity_id.id']))
                    data['name'] = activity.name or '-'
        # attendee's employee_code
        if 'attendee_employee_ids' in data_dict:
            for data in data_dict['attendee_employee_ids']:
                domain = [('employee_code', '=', data.get('employee_code'))]
                data['employee_id.id'] = Employee.search(domain).id
                del data['employee_code']
        # Attachment Links
        file_prefix = self.env.user.company_id.pabiweb_file_prefix
        if file_prefix[-1:] != '/':
            file_prefix += '/'
        if 'attachment_ids' in data_dict:
            for data in data_dict['attachment_ids']:
                data['url'] = file_prefix + data['url']
                data['res_model'] = self._name
                data['type'] = 'url'
                domain = [('employee_code', '=', data.get('attach_by'))]
                data['attach_by.id'] = Employee.search(domain).user_id.id
                del data['attach_by']
        # Web Ref URL
        if 'apweb_ref_url' in data_dict:
            data_dict['apweb_ref_url'] = \
                file_prefix + data_dict['apweb_ref_url']
        return data_dict

    @api.model
    def generate_hr_expense(self, data_dict, test=False):
        _logger.info('generate_hr_expense(), input: %s' % data_dict)
        if not test and not self.env.user.company_id.pabiweb_active:
            raise ValidationError(_('Odoo/PABIWeb Disconnected!'))
        try:
            prepare_code = data_dict.get('preparer_code')
            data_dict = self._pre_process_hr_expense(data_dict)
            res = self.env['pabi.utils.ws'].create_data(self._name, data_dict)
            if res['is_success'] is True:
                expense = self.browse(res['result']['id'])
                self._post_process_hr_expense(expense)
                # Replace Admin with Preparer
                dom = [('employee_code', '=', prepare_code)]
                employee = self.env['hr.employee'].search(dom)
                expense_id = res['result']['id']
                self._cr.execute("""
                    update hr_expense_expense
                    set create_uid = %s, write_uid = %s where id = %s
                """, (employee.user_id.id, employee.user_id.id, expense_id))
                self._cr.execute("""
                    update auditlog_log
                    set user_id = %s where res_id = %s
                    and model_id = (select id from ir_model
                                    where model = 'hr.expense.expense')
                """, (employee.user_id.id, expense_id))
                # --
            self._cr.commit()
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': e,
            }
            self._cr.rollback()
        _logger.info('generate_hr_expense(), input: %s' % res)
        return res

    @api.multi
    def send_signal_to_pabiweb(self, signal, comment=''):
        _logger.info(
            'send_signal_to_pabiweb(), input: [%s, %s]' % (signal, comment))
        self.ensure_one()
        alfresco = self.env['pabi.web.config.settings'].\
            _get_alfresco_connect('exp')
        if alfresco is False:
            return False
        arg = {
            'action': signal,
            'by': self.env.user.login,
            'comment': comment,
        }
        result = False
        if self.is_employee_advance:
            arg.update({'avNo': self.number})
            result = alfresco.brw.action(arg)
        else:
            arg.update({'exNo': self.number})
            result = alfresco.use.action(arg)
        if not result['success']:
            raise ValidationError(
                _("Can't send data to PabiWeb : %s" % (result['message'],))
            )
        _logger.info('send_signal_to_pabiweb(), output: %s' % result)
        return result

    @api.multi
    def send_comment_to_pabiweb(self, status, status_th, comment):
        _logger.info(
            'send_comment_to_pabiweb(), input: [%s, %s, %s]' % (status,
                                                                status_th,
                                                                comment))
        self.ensure_one()
        alfresco = \
            self.env['pabi.web.config.settings']._get_alfresco_connect('exp')
        if alfresco is False:
            return False
        arg = {
            'by': self.env.user.login,
            'task': 'Finance',
            'task_th': u'การเงิน',
            'status': status,
            'status_th': status_th,
            'comment': comment,
        }
        result = False
        if self.is_employee_advance:
            arg.update({'avNo': self.number})
            result = alfresco.brw.history(arg)
        else:
            arg.update({'exNo': self.number})
            result = alfresco.use.history(arg)
        if not result['success']:
            raise ValidationError(
                _("Can't send data to PabiWeb : %s" % (result['message'],))
            )
        _logger.info('send_comment_to_pabiweb(), output: %s' % result)
        return result

    @api.multi
    def write(self, vals):
        res = super(HRExpense, self).write(vals)
        try:
            to_state = vals.get('state', False)
            # if to_state in ('accepted', 'cancelled', 'paid'):
            if to_state in ('accepted', 'cancelled'):
                # signals = {'accepted': '1', 'cancelled': '2', 'paid': '3'}
                signals = {'accepted': '1', 'cancelled': '2'}
                for exp in self:
                    if to_state == 'cancelled':
                        comment = exp.cancel_reason_txt or ''
                        exp.send_signal_to_pabiweb(signals[to_state], comment)
                    else:
                        exp.send_signal_to_pabiweb(signals[to_state])
        except Exception, e:
            self._cr.rollback()
            raise ValidationError(str(e))
        return res
