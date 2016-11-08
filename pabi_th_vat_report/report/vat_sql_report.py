# -*- coding: utf-8 -*-
from openerp import fields, models


class SaleVatReport(models.Model):
    _inherit = 'sale.vat.report'

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Tax Branch'
    )
    taxbranch = fields.Char(
        string='Tax Branch'
    )

    # Methods for create voucher tax query
    def _get_voucher_tax_select(self):
        select_str = super(SaleVatReport, self)._get_voucher_tax_select()
        select_str =\
            select_str + ', avt.taxbranch_id as taxbranch_id, \
            p.taxbranch as taxbranch'
        return select_str

    def _get_voucher_tax_groupby(self):
        voucher_groupby = super(SaleVatReport, self)._get_voucher_tax_groupby()
        voucher_groupby = voucher_groupby + ', avt.taxbranch_id, p.taxbranch'
        return voucher_groupby

    # Methods for create invoice tax query
    def _get_invoice_tax_select(self):
        select_str = super(SaleVatReport, self)._get_invoice_tax_select()
        select_str = select_str + ', ait.taxbranch_id as taxbranch_id,\
        p.taxbranch as taxbranch'
        return select_str

    def _get_invoice_tax_groupby(self):
        invoice_groupby = super(SaleVatReport, self)._get_invoice_tax_groupby()
        invoice_groupby = invoice_groupby + ', ait.taxbranch_id, p.taxbranch'
        return invoice_groupby

    # Methods for create main sql view
    def _get_select(self):
        select_str = super(SaleVatReport, self)._get_select()
        select_str = select_str + ', taxbranch_id, taxbranch'
        return select_str

    def _get_groupby(self):
        groupby_str = super(SaleVatReport, self)._get_groupby()
        groupby_str = groupby_str + ', taxbranch_id, taxbranch'
        return groupby_str


class PurchaseVatReport(models.Model):
    _inherit = 'purchase.vat.report'

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Tax Branch'
    )
    taxbranch = fields.Char(
        string='Tax Branch'
    )

    def _get_select(self):
        select_str = super(PurchaseVatReport, self)._get_select()
        select_str += ', atd.taxbranch_id as taxbranch_id'
        return select_str

    def _get_from(self):
        from_str = super(PurchaseVatReport, self)._get_from()
        from_str += ' LEFT JOIN res_taxbranch t ON (atd.taxbranch_id = t.id)'
        return from_str

    def _get_groupby(self):
        voucher_groupby = super(PurchaseVatReport, self)._get_groupby()
        voucher_groupby += ', atd.taxbranch_id'
        return voucher_groupby
