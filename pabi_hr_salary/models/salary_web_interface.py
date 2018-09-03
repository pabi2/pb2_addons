# -*- coding: utf-8 -*-
import logging
import StringIO
import requests
import ast
import unicodecsv
from openerp import models, api, fields, _
from openerp.exceptions import except_orm, ValidationError
# from .test_data import TEST_DATA

_logger = logging.getLogger(__name__)


class HRSalaryExpense(models.Model):
    _inherit = 'hr.salary.expense'

    @api.multi
    def send_signal_to_pabiweb(self, signal, salary_doc=False):
        _logger.info('send_signal_to_pabiweb(), input: [%s, %s]' %
                     (signal, salary_doc))
        """ Signal: '1' = Submit, '2' = Resubmit, '3' = Cancel
            For 1, 2, require salary_doc """
        self.ensure_one()
        alfresco = \
            self.env['pabi.web.config.settings']._get_alfresco_connect('hr')
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
                'total': str(salary.summary_total or 0.0),
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
        elif result.get('message', False) and \
                'PABIWEB_NUMBER_MISMATCHED' in result['message']:
            _logger.warning(result['message'])
        _logger.info('send_signal_to_pabiweb(), input: %s' % result)
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
        _logger.info('done_salary(), input: %s' % af_info)
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
        salary = self.search([('number', '=', af_info['name'])])
        uid = user.search([('login', '=', af_info['approve_uid'])])
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
        _logger.info('done_salary(), output: %s' % res)
        return res

    @api.multi
    def _prepare_data_to_load(self, datas):
        self.ensure_one()
        """ Change data from REST API to CSV format """
        if not datas:
            return {}
        mapper = {}
        negate = {}
        try:
            mapper = self.env.user.company_id.pabiehr_data_mapper
            mapper = mapper and ast.literal_eval(mapper.strip()) or {}
            negate = self.env.user.company_id.pabiehr_negate_code
            negate = negate and ast.literal_eval(negate.strip()) or {}
        except Exception:
            raise ValidationError(
                _('Odoo & e-HR Mapper Dict is not well formed!'))
        # Special data adjustment. If column 'J' is 31, 50, negate amount
        # negate = {'Q': {'J': ('31', '50')}}
        if negate:
            for d in datas:
                for k, v in negate.iteritems():
                    if d.get(v.keys()[0]) in v.values()[0]:
                        d[k] = "-%s" % d[k]
        # Prepare CSV string
        csv_file = StringIO.StringIO()
        csv_out = unicodecsv.writer(csv_file,
                                    encoding='utf-8',
                                    quoting=unicodecsv.QUOTE_ALL)
        # External ID of this record
        ext_id = self.env['pabi.utils.xls'].get_external_id(self)
        # Write odoo's header columns
        header = [field for field in mapper]
        # first_row = True
        for data in datas:
            line = [mapper[field] and data[mapper[field]] or ''
                    for field in header]
            # ext_id = first_row and ext_id or ''  # external id on 1st row
            line.append(ext_id)
            csv_out.writerow(line)
            # first_row = False  # reset
        csv_file.seek(0)
        csv_txt = csv_file.read()
        csv_file.close()
        header.append('id')  # add external_id column
        return (header, csv_txt)

    @api.model
    def _get_pabiehr_data(self):
        token = self.env['pabi.web.config.settings']._get_pabiehr_connect()
        if token == '':
            raise ValidationError(
                _('Cannot connect with e-HR, please check credential!'))
        elif not token:
            raise ValidationError(
                _('Connection with e-HR is closed!'))
        # Get data
        url = self.env.user.company_id.pabiehr_data_url
        headers = {'Bearer': token}
        response = requests.get(url, headers=headers)
        res = ast.literal_eval(response.text)
        return res

    @api.multi
    def retrieve_data(self):
        self.ensure_one()
        try:
            self.line_ids.unlink()
            # res = TEST_DATA
            res = self._get_pabiehr_data()
            header, csv_txt = self._prepare_data_to_load(res)
            self.env['pabi.utils.xls'].import_csv(self._name, header,
                                                  csv_txt, csv_header=False)
        except KeyError, e:
            raise except_orm(_('Key Error!'), e)
        except Exception, e:
            raise except_orm(_('Error retrieve or loading data!'), e)
        return True
