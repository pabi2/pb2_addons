from openerp import models, fields, api
from openerp.addons import jasper_reports

class InvitedUser_List(models.Model):
    _inherit ='account.vat.report'
    
    @api.multi
    def print_report(self):
        data = self.read([])[0]
        data.update({'test':22})
#         print"data-------------------",data
        record_id = self.id
#         print"record_id-------------------------------",record_id
        context = self._context.copy()
#         print"context---------------------------",context
        context.update({'xls_export': True})
        report_name = self.print_format == 'excel' and 'vat_report_xls' or \
            'vat_report_pdf'
        tax_details = self.get_lines(record_id)
        print"tax_details-------------------",tax_details
        Report = self.env['account.vat.report']
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
        }
        return res

    def get_lines(self, record):
#         print"record-----------------------",record
        record_id = self.env['account.vat.report'].browse(record)
#         print"record_id++++++++++++++++++++++",record_id.tax_id.type_tax_use,record_id
        tax_details = []
        if record_id.tax_id.type_tax_use == 'sale':
            tax_details = self._get_tax_lines(record_id, 'sale.vat.report')
        if record_id.tax_id.type_tax_use == 'purchase':
            tax_details = self._get_tax_lines(record_id, 'purchase.vat.report')
        if record_id.tax_id.type_tax_use == 'all':
            tax_details = \
                self._get_customer_tax_lines(record_id) + \
                self._get_supplier_tax_lines(record_id)
        self.total_tax = sum(res['tax_amount'] for res in tax_details)
        self.total_base = sum(res['base_amount'] for res in tax_details)
        return tax_details
    
    def _get_tax_lines(self, record, model):
        domain = self._get_domain_tax_lines(record)
#         print"domain---------------------------",domain
        tax_lines = self.env[model].search_read(domain)
#         print"tax_lines--------------------------------",tax_lines
        return tax_lines
    
    def _get_domain_tax_lines(self, record):
        domain = [('base_code_id', '=', record.base_code_id.id),
                  ('tax_code_id', '=', record.tax_code_id.id),
                  ('period_id', '=', record.period_id.id),
                  ('company_id', '=', record.company_id.id)]
        return domain
