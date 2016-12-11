# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from .account_tax_detail import InvoiceVoucherTaxDetail


class AccountVoucher(InvoiceVoucherTaxDetail, models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def proforma_voucher(self):
        result = super(AccountVoucher, self).proforma_voucher()
        if self.type == 'receipt' or \
                self.env.user.company_id.auto_recognize_vat or \
                self._context.get('recognize_vat', False):
            self._compute_sales_tax_detail()
            self._check_tax_detail_info()
            self._assign_detail_tax_sequence()
        return result

    @api.multi
    def action_cancel_draft(self):
        for rec in self:
            for voucher_tax in rec.tax_line_normal:
                # Delete and recreate tax detail
                voucher_tax.detail_ids.unlink()
                if voucher_tax.tax_code_type == 'normal':
                    detail = voucher_tax._prepare_voucher_tax_detail()
                    self.env['account.tax.detail'].create(detail)
        res = super(AccountVoucher, self).action_cancel_draft()
        return res

    @api.multi
    def cancel_voucher(self):
        for rec in self:
            for voucher_tax in rec.tax_line_normal:
                voucher_tax.detail_ids.write({'cancel': True})
        res = super(AccountVoucher,
                    self.with_context(no_reset_tax=True)).cancel_voucher()
        return res


class AccountVoucherTax(models.Model):
    _inherit = 'account.voucher.tax'

    detail_ids = fields.One2many(
        'account.tax.detail',
        'voucher_tax_id',
        string='Tax Detail',
    )

    @api.model
    def _prepare_voucher_tax_detail(self):
        currency = self.voucher_id.journal_id.currency
        ttype = self.voucher_id.type
        doc_type = ttype == 'receipt' and 'sale' or 'purchase'
        return {'doc_type': doc_type,
                'currency_id': currency.id,
                'voucher_tax_id': self.id}

    @api.model
    def create(self, vals):
        voucher_tax = super(AccountVoucherTax, self).create(vals)
        if voucher_tax.tax_code_type == 'normal':
            detail = voucher_tax._prepare_voucher_tax_detail()
            self.env['account.tax.detail'].create(detail)
        return voucher_tax

    @api.model
    def move_line_get(self, voucher):
        res = super(AccountVoucherTax, self).move_line_get(voucher)
        # Add Tax Difference
        self._cr.execute("""
            select -coalesce(
                (select sum(amount) amount from account_voucher_tax
                where tax_code_type = 'normal' and voucher_id = %s) +
                (select sum(amount) amount from account_voucher_tax
                where tax_code_type = 'undue' and voucher_id = %s), 0.0)
        """, (voucher.id, voucher.id))
        vat_diff = self._cr.fetchone()[0] or 0.0
        if vat_diff:
            account = self.env.user.company_id.account_tax_difference
            if not account:
                raise ValidationError(_('No Tax Difference Account!'))
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
