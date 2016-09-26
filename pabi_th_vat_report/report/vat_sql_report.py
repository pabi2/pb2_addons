# -*- coding: utf-8 -*-
from openerp import fields, models


class VatReport(models.Model):
    _inherit = 'vat.report'

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Tax Branch'
    )
    taxbranch = fields.Char(
        string='Tax Branch'
    )

    # Methods for create voucher tax query
    def _get_voucher_tax_select(self):
        select_str = super(VatReport, self)._get_voucher_tax_select()
        select_str =\
            select_str + ', avt.taxbranch_id as taxbranch_id, \
            p.taxbranch as taxbranch'
        return select_str

    def _get_voucher_tax_groupby(self):
        voucher_groupby = super(VatReport, self)._get_voucher_tax_groupby()
        voucher_groupby = voucher_groupby + ', avt.taxbranch_id, p.taxbranch'
        return voucher_groupby

    # Methods for create invoice tax query
    def _get_invoice_tax_select(self):
        select_str = super(VatReport, self)._get_invoice_tax_select()
        select_str = select_str + ', ait.taxbranch_id as taxbranch_id,\
        p.taxbranch as taxbranch'
        return select_str

    def _get_invoice_tax_groupby(self):
        invoice_groupby = super(VatReport, self)._get_invoice_tax_groupby()
        invoice_groupby = invoice_groupby + ', ait.taxbranch_id, p.taxbranch'
        return invoice_groupby

    # Methods for create main sql view
    def _get_select(self):
        select_str = super(VatReport, self)._get_select()
        select_str = select_str + ', taxbranch_id, taxbranch'
        return select_str

    def _get_groupby(self):
        groupby_str = super(VatReport, self)._get_groupby()
        groupby_str = groupby_str + ', taxbranch_id, taxbranch'
        return groupby_str
