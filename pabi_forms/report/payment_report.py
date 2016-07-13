# -*- coding: utf-8 -*-
from openerp.report import report_sxw
from openerp.osv import osv


class PaymentReportParser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(PaymentReportParser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_currency_rate': self.get_currency_rate,
            'get_invoices': self.get_invoices,
        })

    def get_invoices(self, lines):
        invoices = []
        for line in lines:
            if line.amount > 0.0:
                invoices.append(line.move_line_id.invoice.id)
        return len(invoices)

    def get_currency_rate(self, currency, date):
        context = self.localcontext.copy()
        context.update({'date': date})
        rate = self.pool['res.currency']._get_current_rate(self.cr, self.uid, [currency.id], raise_on_no_rate=True, context=context)
        rate = rate[currency.id]
        return rate


class PaymentReportAbstarct(osv.AbstractModel):
    _name = "report.pabi_forms.account_supplier_payment_lang"
    _inherit = "report.abstract_report"
    _template = "pabi_forms.account_supplier_payment_lang"
    _wrapped_report_class = PaymentReportParser

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
