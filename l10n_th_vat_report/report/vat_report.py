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

    def _get_customer_tax_lines(self, record):
        domain = [('base_code_id', '=', record.base_code_id.id),
                  ('tax_code_id', '=', record.tax_code_id.id),
                  ('period_id', '=', record.period_id.id),
                  ('company_id', '=', record.company_id.id)]
        tax_lines =\
            self.pool['vat.report'].search_read(self.cr, self.uid, domain)
        return tax_lines

    def _get_select_tax_details(self):
        select_str = """
            atd.id,
            p.name as partner_name,
            p.vat as tax_id,
            atd.invoice_date as date,
            atd.invoice_number as number,
            COALESCE(SUM(atd.amount), 0.0) as tax_amount,
            COALESCE(SUM(atd.base), 0.0) as base_amount,
            atd.tax_sequence as tax_sequence
        """
        return select_str

    def _get_from_tax_details(self):
        from_tax_details = """
                account_tax_detail as atd
            LEFT JOIN account_invoice_tax ait ON
                (atd.invoice_tax_id = ait.id)
            LEFT JOIN account_voucher_tax avt ON
                (atd.voucher_tax_id = avt.id)
            LEFT JOIN account_invoice invoice ON
                (ait.invoice_id = invoice.id)
            LEFT JOIN account_voucher voucher ON
                (avt.voucher_id = voucher.id)
            LEFT JOIN res_partner p ON
                (atd.partner_id = p.id)
        """
        return from_tax_details

    def _get_where_tax_details(self, record):
        where_tax_details = """
            atd.tax_sequence IS NOT NULL AND
            atd.period_id = %s AND
            ((ait.base_code_id = %s) OR (avt.base_code_id = %s)) AND
            ((ait.tax_code_id = %s) OR (avt.tax_code_id = %s)) AND
            ((ait.company_id = %s) OR (avt.company_id = %s)) AND
            ((invoice.state in ('open', 'paid')) OR
            (voucher.state in ('posted')))
        """ % (
               record.period_id.id,
               record.base_code_id.id, record.base_code_id.id,
               record.tax_code_id.id, record.tax_code_id.id,
               record.company_id.id, record.company_id.id)
        return where_tax_details

    def _get_groupby_tax_details(self):
        groupby_str = """
            atd.id,
            atd.invoice_date,
            atd.invoice_number,
            p.name,
            p.vat
        """
        return groupby_str

    def _get_supplier_tax_lines(self, record):
        self.cr.execute("""
            SELECT
                %s
            FROM
                %s
            WHERE
                %s
            GROUP BY
                %s
        """ % (self._get_select_tax_details(),
               self._get_from_tax_details(),
               self._get_where_tax_details(record),
               self._get_groupby_tax_details()))
        tax_details = self.cr.dictfetchall()
        return tax_details

    def get_lines(self, record):
        tax_details = []
        if record.tax_id.type_tax_use == 'sale':
            tax_details = self._get_customer_tax_lines(record)
        if record.tax_id.type_tax_use == 'purchase':
            tax_details = self._get_supplier_tax_lines(record)
        if record.tax_id.type_tax_use == 'all':
            tax_details =\
                self._get_customer_tax_lines(record) +\
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
