# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountTaxReportWizard(models.TransientModel):
    _name = 'account.tax.report.wizard'

    period_id = fields.Many2one(
        'account.period',
        string='Period',
        related='calendar_period_id.period_id',
    )
    calendar_period_id = fields.Many2one(
        'account.period.calendar',
        string='Calendar Period',
        required=True,
    )
    tax_id = fields.Many2one(
        'account.tax',
        string='Tax',
        required=True,
        domain=[('type_tax_use', '!=', 'all'),
                ('is_wht', '=', False),
                ('is_undue_tax', '=', False)],
    )
    print_format = fields.Selection(
        [('pdf', 'PDF'),
         ('xls', 'Excel')],
        string='Print Format',
        default='pdf',
        required=True,
    )

    @api.multi
    def run_report(self):
        data = {'parameters': {}}
        report_name = self.print_format == 'pdf' and \
            'account_tax_report_pdf' or 'account_tax_report_xls'
        period = self.calendar_period_id.period_id
        # Params
        data['parameters']['report_period_id'] = period.id
        data['parameters']['tax_id'] = self.tax_id.id
        data['parameters']['doc_type'] = self.tax_id.type_tax_use
        # Display Params
        company = self.env.user.company_id.partner_id
        company_name = company.name or ''
        data['parameters']['company_name'] = company.title.name and \
            company.title.name + ' ' + company_name or company_name
        data['parameters']['branch_name'] = data['parameters']['company_name']
        data['parameters']['branch_vat'] = company.vat or ''
        data['parameters']['branch_taxbranch'] = company.taxbranch or ''
        data['parameters']['advance_sequence'] = False
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
        }
        return res
