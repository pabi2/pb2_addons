# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.l10n_th_account.models.res_partner \
    import INCOME_TAX_FORM


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
        required=True,
    )

    @api.multi
    def run_report(self):
        data = {'parameters': {}}
        report_name = False
        ids = []
        if self.income_tax_form == 'pnd53':
            report_name = 'report_pnd53_form'
        if self.income_tax_form == 'pnd3':
            report_name = 'report_pnd3_form'
        if not report_name:
            raise ValidationError(_('Selected form not found!'))
        # For ORM, we search for ids, and only pass ids to parser and jasper
        domain = [
            ('income_tax_form', '=', self.income_tax_form),
            ('wht_period_id', '=', self.calendar_period_id.period_id.id),
        ]
        ids = self.env['report.pnd.form'].search(domain)._ids
        data['parameters']['ids'] = ids
        company = self.env.user.company_id.partner_id
        company_taxid = len(company.vat) == 13 and company.vat or ''
        company_branch = \
            len(company.taxbranch) == 5 and company.taxbranch or ''
        data['parameters']['company_taxid'] = company_taxid
        data['parameters']['company_branch'] = company_branch
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
        }
        print res
        return res
