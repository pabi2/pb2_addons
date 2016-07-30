# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from .account_tax_detail import InvoiceVoucherTaxDetail


class AccountVoucher(InvoiceVoucherTaxDetail, models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def proforma_voucher(self):
        result = super(AccountVoucher, self).proforma_voucher()
        self._check_tax_detail_info()
        self._assign_detail_tax_sequence()
        return result


class AccountVoucherTax(models.Model):
    _inherit = 'account.voucher.tax'

    detail_ids = fields.One2many(
        'account.tax.detail',
        'voucher_tax_id',
        string='Tax Detail',
    )

    @api.model
    def create(self, vals):
        voucher_tax = super(AccountVoucherTax, self).create(vals)
        detail = {'voucher_tax_id': voucher_tax.id}
        self.env['account.tax.detail'].create(detail)
        return voucher_tax

    @api.model
    def move_line_get(self, voucher_id):
        res = super(AccountVoucherTax, self).move_line_get(voucher_id)
        # Add Tax Difference
        self._cr.execute("""
            select -coalesce(
                (select sum(amount) amount from account_voucher_tax
                where tax_code_type = 'normal' and voucher_id = %s) +
                (select sum(amount) amount from account_voucher_tax
                where tax_code_type = 'undue' and voucher_id = %s), 0.0)
        """, (voucher_id, voucher_id))
        vat_diff = self._cr.fetchone()[0] or 0.0
        if vat_diff:
            voucher = self.env['account.voucher'].browse(voucher_id)
            account = voucher.partner_id.property_account_tax_difference
            res.append({
                'type': 'tax',
                'name': _('Tax Difference'),
                'price_unit': vat_diff,
                'quantity': 1,
                'price': vat_diff,
                'account_id': account.id,
            })
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
