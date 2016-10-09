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


class VatReportAbstarct(osv.AbstractModel):
    _name = "report.l10n_th_vat_report.report_vat"
    _inherit = "report.abstract_report"
    _template = "l10n_th_vat_report.report_vat"
    _wrapped_report_class = VatReportParser

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
