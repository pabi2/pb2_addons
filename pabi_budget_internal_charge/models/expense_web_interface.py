# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.model
    def _post_process_hr_expense(self, expense):
        if expense.internal_charge:  # Case internal charge, auto confirm
            expense.signal_workflow('confirm')
            if self._context.get('auto_confirm_internal_charge'):
                # Use sudo as this is called form Alfresco
                expense.sudo().signal_workflow('internal_charge')
        else:
            super(HRExpense, self)._post_process_hr_expense(expense)

    @api.model
    def test_generate_internal_charge(self):
        """ This will create Internal Charge, and approve -> paid in 1 step """
        data_dict = {
            'internal_section_id': u'100029',  # Internal charge section
            'internal_project_id': False,  # Internal charge project
            'employee_id': u'001509',  # Requester (employee), name or code
            'user_id': u'001509',  # Preparer (user), name or code
            'approver_id': u'001509',  # Approver (user), name or code
            'date': u'2018-10-30',  # Approve Date YYYY-MM-DD
            'name': u'Description field',  # Description
            'note': u'Buttom notes',  # Note at bottom of screen
            'line_ids': [
                {
                    'activity_group_id': u'การจัดประชุม',
                    'activity_id': u'ค่าเช่าเครื่องมือห้องปฏิบัติการ',
                    'name': u'Line Description 1',
                    'section_id': u'100005',  # Section or Project
                    'project_id': False,
                    'cost_control_id': False,
                    'unit_amount': 100000.00,
                },
                {
                    'activity_group_id': u'การจัดประชุม',
                    'activity_id': u'ค่าเช่าเครื่องมือห้องปฏิบัติการ',
                    'name': u'Line Description 1',
                    'section_id': u'100005',  # Section or Project
                    'project_id': False,
                    'cost_control_id': False,
                    'uni_amount': 100000,
                    'unit_amount': 100000.00,
                },
            ],
        }
        return self.generate_internal_charge(data_dict,
                                             auto_confirm=True,
                                             test=True)  # No need for prod.

    @api.model
    def generate_internal_charge(self, data_dict,
                                 auto_confirm=False,
                                 test=False):
        if not test and not self.env.user.company_id.pabiweb_active:
            raise ValidationError(_('Odoo/PABIWeb Disconnected!'))
        try:
            User = self.env['res.users']
            user_id = User.name_search(data_dict.get('user_id'))[0][0]
            user = User.browse(user_id)
            # Set internal charge related info header
            data_dict.update({
                'pay_to': 'internal',
                'is_advance_clearing': False,
                'is_employee_advance': False,
                'number': u'/',  # expense number
                'operating_unit_id': user.default_operating_unit_id.id,
            })
            WS = self.env['pabi.utils.ws']
            res = WS.sudo().friendly_create_data(self._name, data_dict)
            if res['is_success']:
                expense_id = res['result']['id']
                expense = self.browse(expense_id)
                res['result']['number'] = expense.number
                # Post document
                self.with_context(auto_confirm_internal_charge=auto_confirm).\
                    _post_process_hr_expense(expense)
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': e,
            }
            self._cr.rollback()
        return res
