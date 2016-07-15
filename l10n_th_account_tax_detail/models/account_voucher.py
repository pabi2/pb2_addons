# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil import relativedelta
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from .account_tax_detail import InvoiceVoucherTaxDetail


class AccountVoucher(InvoiceVoucherTaxDetail, models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def proforma_voucher(self):
        self._check_tax_detail_info()
        result = super(AccountVoucher, self).proforma_voucher()
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
