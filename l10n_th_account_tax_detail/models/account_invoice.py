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
    def action_number(self):
        result = super(AccountInvoice, self).action_number()
        self._compute_sales_tax_detail()
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
    def _prepare_invoice_tax_detail(self, invoice_tax):
        ttype = invoice_tax.invoice_id.type
        doc_type = \
            ttype in ('out_invoice', 'out_refund') and 'sale' or 'purchase'
        return {'doc_type': doc_type,
                'invoice_tax_id': invoice_tax.id}

    @api.model
    def create(self, vals):
        invoice_tax = super(AccountInvoiceTax, self).create(vals)
        if invoice_tax.tax_code_type == 'normal':
            detail = self._prepare_invoice_tax_detail(invoice_tax)
            self.env['account.tax.detail'].create(detail)
        return invoice_tax

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
