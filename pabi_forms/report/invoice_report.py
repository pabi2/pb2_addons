# -*- coding: utf-8 -*-
from openerp.report import report_sxw
from openerp.osv import osv


class InvoiceReportParser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(InvoiceReportParser, self).__init__(cr, uid, name,
                                                  context=context)
        self.localcontext.update({
            'get_currency_rate': self.get_currency_rate,
            'get_doc_ref': self.get_doc_ref,
        })

    def get_doc_ref(self, invoice):
        header_text = ''
        for tax in invoice.tax_line:
            for detail in tax.detail_ids:
                if not header_text:
                    header_text = detail.invoice_number
                else:
                    header_text = (header_text + ',' +
                                   detail.invoice_number)
        return header_text

    def get_currency_rate(self, currency, date):
        user = self.pool['res.users'].browse(self.cr, self.uid, self.uid)
        company = user.company_id
        context = self.localcontext.copy()
        context.update({'date': date})
        # get rate of company currency to current invoice currency
        rate = self.pool['res.currency'].\
            _get_conversion_rate(self.cr, self.uid,
                                 company.currency_id,
                                 currency, context=context)
        return rate


class InvoiceReportAbstarct(osv.AbstractModel):
    _name = "report.pabi_forms.account_supplier_invoices_lang"
    _inherit = "report.abstract_report"
    _template = "pabi_forms.account_supplier_invoices_lang"
    _wrapped_report_class = InvoiceReportParser
