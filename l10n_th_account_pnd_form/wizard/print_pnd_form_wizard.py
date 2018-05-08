# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.l10n_th_account.models.res_partner \
    import INCOME_TAX_FORM

REPORT_NAMES = {
    'pnd1': {'pdf': False,  # TODO: pnd1
             'xls': False,
             'txt_csv': False},
    'pnd53': {'pdf': 'report_pnd53_form',
              'xls': 'report_pnd53_form_xls',
              'txt_csv': 'report_pnd53_form_txt'},
    'pnd3': {'pdf': 'report_pnd3_form',
             'xls': 'report_pnd3_form_xls',
             'txt_csv': 'report_pnd3_form_txt'},
    'pnd3a': {'pdf': 'report_pnd3a_form',
              'xls': 'report_pnd3a_form_xls',
              'txt_csv': 'report_pnd3a_form_txt'}, }


class PrintPNDFormWizard(models.TransientModel):
    _name = 'print.pnd.form.wizard'

    income_tax_form = fields.Selection(
        INCOME_TAX_FORM,
        string='Income Tax Form',
        required=True,
    )
    calendar_period_id = fields.Many2one(
        'account.period.calendar',
        string='Calendar Period',
        required=False,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscalyear',
        required=False,
    )
    print_format = fields.Selection(
        [('pdf', 'PDF'),
         ('xls', 'XLS'),
         ('txt_csv', 'TXT')],
        string='Print Format',
        default='pdf',
        required=True,
    )

    @api.multi
    def run_report(self):
        report_name = REPORT_NAMES[self.income_tax_form][self.print_format]
        if not report_name:
            raise ValidationError(_('Selected form not found!'))
        company = self.env.user.company_id.partner_id
        company_taxid = len(company.vat or '') == 13 and company.vat or ''
        company_branch = \
            len(company.taxbranch or '') == 5 and company.taxbranch or ''
        # Params to Jasper
        data_dict = {
            'no_header': self.print_format == 'txt_csv' and True or False,
            'income_tax_form': (self.income_tax_form == 'pnd3a' and
                                'pnd3' or self.income_tax_form),
            'fiscalyear_id': self.fiscalyear_id.id,
            'wht_period_id': self.calendar_period_id.id,
            'company_taxid': company_taxid,
            'company_branch': company_branch,
            'print_name': self.env.user.name or '',
            'print_position': self.env.user.employee_id.job_id.name or ''
        }
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': {'parameters': data_dict},
            'context': {'lang': 'th_TH'},
        }
        return res
