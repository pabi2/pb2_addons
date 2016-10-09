# -*- coding: utf-8 -*-
from openerp.report import report_sxw
from openerp.osv import osv


class PaymentReportParser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(PaymentReportParser, self).__init__(cr, uid, name,
                                                  context=context)
        self.localcontext.update({
            'get_currency_rate': self.get_currency_rate,
            'get_invoices': self.get_invoices,
        })

    def get_invoices(self, lines):
        count = 0
        inv_str = False
        for line in lines:
            if line.amount > 0.0:
                if line.move_line_id.invoice:
                    if not inv_str:
                        inv_str = str(count + 1) + ':' +\
                            line.move_line_id.invoice.number + '\n'
                    else:
                        inv_str += str(count + 1) + ':' +\
                            line.move_line_id.invoice.number + '\n'
                    count += 1
        return inv_str and inv_str or ''

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


class PaymentReportAbstarct(osv.AbstractModel):
    _name = "report.pabi_forms.account_supplier_payment_lang"
    _inherit = "report.abstract_report"
    _template = "pabi_forms.account_supplier_payment_lang"
    _wrapped_report_class = PaymentReportParser

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
