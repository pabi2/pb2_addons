# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
import xmlrpclib


class HRSalaryExpense(models.Model):
    _inherit = 'hr.salary.expense'

    @api.model
    def _get_alfresco_connect(self):
        ConfParam = self.env['ir.config_parameter']
        pabiweb_active = self.env.user.company_id.pabiweb_active
        if not pabiweb_active:
            return False
        url = self.env.user.company_id.pabiweb_hr_url
        username = self.env.user.login
        password = ConfParam.get_param('pabiweb_password')
        connect_string = url % (username, password)
        alfresco = xmlrpclib.ServerProxy(connect_string)
        return alfresco

    @api.multi
    def send_signal_to_pabiweb(self, signal, salary_doc=False):
        """ Signal: '1' = Submit, '2' = Resubmit, '3' = Cancel
            For 1, 2, require salary_doc """
        self.ensure_one()
        alfresco = self._get_alfresco_connect()
        if alfresco is False:
            return False
        arg = {}
        salary = self
        user = self.env.user
        section = self.env.user.partner_id.employee_id.section_id
        if signal in ('1', '2'):  # Start or Resubmit
            if not salary_doc:
                raise ValidationError(_('Salary document not found'))
            other_docs = self.env['ir.attachment'].search([
                ('id', '!=', salary_doc.id),
                ('res_id', '=', self.id),
                ('res_model', '=', 'hr.salary.expense'),
            ])
            attachments = [{'name': doc.name, 'content': doc.datas}
                           for doc in other_docs]
            arg = {
                'action': signal,
                'salaryNo': salary.number,
                'sectionId': str(section.id),
                'objective': salary.name,
                'total': str(salary.amount_total or 0.0),
                'reqBy': user.login,
                'doc': {'name': salary_doc.name,
                        'content': salary_doc.datas},
                'attachments': attachments
            }
        elif signal == '3':  # Cancel
            arg = {
                'action': signal,
                'salaryNo': salary.number,
                'comment': u'',  # Not implemented yet.
                'reqBy': user.login,
            }
        else:
            raise ValidationError(_('Wrong PABIWeb Signal!'))
        result = alfresco.sal.action(arg)
        if not result['success']:
            raise ValidationError(
                _("Can't send data to PabiWeb : %s" % (result['message'],))
            )
        return result

    @api.model
    def test_done_salary(self):
        af_info = {
            'name': 'SLR/003',
            'approve_uid': '000377',
            'action': 'C1',
            'file_name': 'TE00017.pdf',
            'file_url': 'SLR_003.pdf',
            'comment': 'reject reason',
        }
        return self.done_salary(af_info)

    @api.model
    def done_salary(self, af_info):
        """ af_info = {
            'name': 'SAL0001',
            'approve_uid': '000377',
            'action' : 'C1' or 'W2'
            'file_name': 'TE00017.pdf',
            'file_url': 'aaaaas.pdf',
            'comment': 'reject reason',
        }"""
        user = self.env['res.users']
        res = {}
        print af_info
        salary = self.search([('number', '=', af_info['name'])])
        uid = user.search([('login', '=', af_info['approve_uid'])])
        print uid
        print salary
        if len(salary) != 1:
            res.update({
                'is_success': False,
                'result': False,
                'messages': _('Cannot verify salary request!'),
            })
            return res
        try:
            if af_info['action'] == 'C1':  # approve
                # Add returned attachment
                file_prefix = self.env.user.company_id.pabiweb_file_prefix
                self.env['ir.attachment'].create({
                    'res_id': salary.id,
                    'res_model': 'hr.salary.expense',
                    'name': af_info['file_name'],
                    'url': file_prefix + af_info['file_url'],
                    'type': 'url',
                })
                # Change states
                print uid.id
                salary.write({
                    'approve_user_id': uid.id,
                    'date_approve': fields.Date.context_today(self),
                    'state': 'approve',
                })
            else:  # reject (W1)
                salary.write({
                    'note': af_info['comment'],
                    'state': 'reject'
                })
            res.update({
                'is_success': True,
                'result': True,
            })
        except Exception, e:
            res.update({
                'is_success': False,
                'result': False,
                'messages': _(str(e)),
            })
        return res
