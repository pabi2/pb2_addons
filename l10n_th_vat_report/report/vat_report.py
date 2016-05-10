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

    def get_voucher_tax(self, record):
        """Prepare the report data from account_voucher_tax
            base on selected tax, tax code, base code,
            company and period on wizard.
            :param recordset record: record of current wizard
            :return: list of dictionary of value to print report
        """
        period = record.period_id
        company = record.company_id
        tax = record.tax_id
        base_code = record.base_code_id
        tax_code = record.tax_code_id

        self.cr.execute("""
            SELECT
                avt.id,
                CASE WHEN voucher.state = 'cancel' THEN 0.0
                    ELSE SUM(avt.base_amount) END as base_amount,
                CASE WHEN voucher.state = 'cancel' THEN 0.0
                    ELSE SUM(avt.tax_amount) END as tax_amount,
                voucher.date as date,
                CASE WHEN voucher.state = 'cancel'
                    THEN voucher.number || ' (CANCELLED)'
                    ELSE voucher.number END as number,
                p.name as partner_name,
                p.vat as tax_id,
                avt.tax_id as tax
            FROM
                account_voucher_tax as avt
            LEFT JOIN account_voucher voucher ON
                (avt.voucher_id = voucher.id)
            LEFT JOIN res_partner p ON
                (voucher.partner_id = p.id)
            WHERE
                voucher.state in ('cancel', 'posted') AND
                avt.tax_id = %s AND
                avt.base_code_id = %s AND
                avt.tax_code_id = %s AND
                voucher.period_id = %s AND
                avt.company_id =%s
            GROUP BY
                voucher.state,avt.id,voucher.date,voucher.number,p.name,p.vat,avt.tax_id
        """, (tax.id, base_code.id, tax_code.id, period.id, company.id))
        voucher_tax = self.cr.dictfetchall()
        return voucher_tax

    def get_invoice_tax(self, record):
        """Prepare the report data from account_invoice_tax
            base on selected tax code, base code,
            company and period on wizard.
            :param recordset record: record of current wizard
            :return: list of dictionary of value to print report
        """
        period = record.period_id
        company = record.company_id
        base_code = record.base_code_id
        tax_code = record.tax_code_id

        self.cr.execute("""
            SELECT
                ait.id,
                CASE WHEN invoice.state = 'cancel' THEN 0.0
                    ELSE SUM(ait.base_amount) END as base_amount,
                CASE WHEN invoice.state = 'cancel' THEN 0.0
                    ELSE SUM(ait.tax_amount) END as tax_amount,
                invoice.date_invoice as date,
                CASE WHEN invoice.state = 'cancel'
                    THEN invoice.internal_number || ' (CANCELLED)'
                    ELSE invoice.internal_number END as number,
                p.name as partner_name,
                p.vat as tax_id
            FROM
                account_invoice_tax as ait
            LEFT JOIN account_invoice invoice ON
                (ait.invoice_id = invoice.id)
            LEFT JOIN res_partner p ON
                (invoice.partner_id = p.id)
            WHERE
                invoice.state in ('cancel', 'open', 'paid') AND
                invoice.internal_number is not null AND
                ait.base_code_id = %s AND
                ait.tax_code_id = %s AND
                invoice.period_id = %s AND
                ait.company_id =%s
            GROUP BY
                invoice.state,ait.id,invoice.date_invoice,invoice.internal_number,p.name,p.vat
        """, (base_code.id, tax_code.id, period.id, company.id))
        invoice_tax = self.cr.dictfetchall()
        return invoice_tax

    def get_lines(self, record):
        result = []
        voucher_tax = self.get_voucher_tax(record)
        result.extend(voucher_tax)
        invoice_tax = self.get_invoice_tax(record)
        result.extend(invoice_tax)
        self.total_tax = sum(res['tax_amount'] for res in result)
        self.total_base = sum(res['base_amount'] for res in result)
        return result


class VatReportAbstarct(osv.AbstractModel):
    _name = "report.l10n_th_vat_report.report_vat"
    _inherit = "report.abstract_report"
    _template = "l10n_th_vat_report.report_vat"
    _wrapped_report_class = VatReportParser

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
