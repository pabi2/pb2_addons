# -*- coding: utf-8 -*-
from openerp.osv import osv

import openerp.addons.l10n_th_vat_report.report.vat_report as vat_report


class VatReportParser(vat_report.VatReportParser):
    def __init__(self, cr, uid, name, context):
        super(VatReportParser, self).__init__(cr, uid, name, context=context)

    def _get_domain_tax_lines(self, record):
        domain = super(VatReportParser, self)._get_domain_tax_lines(record)
        domain.append(('taxbranch_id', '=', record.taxbranch_id.id))
        return domain

    def _get_from_tax_details(self):
        res = super(VatReportParser, self)._get_from_tax_details()
        res = res + 'LEFT JOIN res_taxbranch t ON (atd.taxbranch_id = t.id)'
        return res

    def _get_groupby_tax_details(self):
        res = super(VatReportParser, self)._get_groupby_tax_details()
        res = res + ', p.taxbranch'
        return res

    def _get_select_tax_details(self):
        res = super(VatReportParser, self)._get_select_tax_details()
        res = res + ',p.taxbranch as taxbranch'
        return res

    def _get_where_tax_details(self, record):
        res = super(VatReportParser, self)._get_where_tax_details(record)
        res = res + 'AND atd.taxbranch_id = %s' % (record.taxbranch_id.id)
        return res


class VatReportAbstarct(osv.AbstractModel):
    _name = "report.l10n_th_vat_report.report_vat"
    _inherit = "report.abstract_report"
    _template = "l10n_th_vat_report.report_vat"
    _wrapped_report_class = VatReportParser

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
