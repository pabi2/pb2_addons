# -*- coding: utf-8 -*-
from openerp.report import report_sxw
from openerp.osv import osv


class InvoiceReportParser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(InvoiceReportParser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_currency_rate': self.get_currency_rate
        })

    def get_currency_rate(self, currency, date):
        context = self.localcontext.copy()
        context.update({'date': date})
        rate = self.pool['res.currency']._get_current_rate(self.cr, self.uid, [currency.id], raise_on_no_rate=True, context=context)
        rate = rate[currency.id]
        return rate


class InvoiceReportAbstarct(osv.AbstractModel):
    _name = "report.pabi_forms.account_supplier_invoices_lang"
    _inherit = "report.abstract_report"
    _template = "pabi_forms.account_supplier_invoices_lang"
    _wrapped_report_class = InvoiceReportParser

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
