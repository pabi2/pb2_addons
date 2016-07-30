# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .account_tax_detail import InvoiceVoucherTaxDetail


class AccountInvoice(InvoiceVoucherTaxDetail, models.Model):
    _inherit = 'account.invoice'

    @api.model
    def check_missing_tax(self):
        res = False  # Force not check missing tax
        return res

    @api.multi
    def action_move_create(self):
        result = super(AccountInvoice, self).action_move_create()
        self._check_tax_detail_info()
        self._assign_detail_tax_sequence()
        return result


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    detail_ids = fields.One2many(
        'account.tax.detail',
        'invoice_tax_id',
        string='Tax Detail',
    )

    @api.model
    def create(self, vals):
        invoice_tax = super(AccountInvoiceTax, self).create(vals)
        detail = {'invoice_tax_id': invoice_tax.id}
        self.env['account.tax.detail'].create(detail)
        return invoice_tax

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
