# -*- coding: utf-8 -*-
from openerp.report import report_sxw
from openerp.osv import osv


class VatReportParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(VatReportParser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_lines': self.get_lines,
            'get_base_total': self.get_base_total,
            'get_tax_total': self.get_tax_total
        })
        self.total_tax = 0.0
        self.total_base = 0.0

    def get_base_total(self):
        return self.total_base

    def get_tax_total(self):
        return self.total_tax

    def _get_domain_tax_lines(self, record):
        domain = [('base_code_id', '=', record.base_code_id.id),
                  ('tax_code_id', '=', record.tax_code_id.id),
                  ('period_id', '=', record.period_id.id),
                  ('company_id', '=', record.company_id.id)]
        return domain

    def _get_tax_lines(self, record, model):
        domain = self._get_domain_tax_lines(record)
        tax_lines = self.pool[model].search_read(self.cr, self.uid, domain)
        return tax_lines

    def get_lines(self, record):
        tax_details = []
        if record.tax_id.type_tax_use == 'sale':
            tax_details = self._get_tax_lines(record, 'sale.vat.report')
        if record.tax_id.type_tax_use == 'purchase':
            tax_details = self._get_tax_lines(record, 'purchase.vat.report')
        if record.tax_id.type_tax_use == 'all':
            tax_details = \
                self._get_customer_tax_lines(record) + \
                self._get_supplier_tax_lines(record)
        self.total_tax = sum(res['tax_amount'] for res in tax_details)
        self.total_base = sum(res['base_amount'] for res in tax_details)
        return tax_details


class VatReportAbstarct(osv.AbstractModel):
    _name = "report.l10n_th_vat_report.report_vat"
    _inherit = "report.abstract_report"
    _template = "l10n_th_vat_report.report_vat"
    _wrapped_report_class = VatReportParser

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
