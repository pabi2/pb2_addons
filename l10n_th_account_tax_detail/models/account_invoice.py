# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .account_tax_detail import InvoiceVoucherTaxDetail


class AccountInvoice(InvoiceVoucherTaxDetail, models.Model):
    _inherit = 'account.invoice'

    # If specified, will be used for sales tax detail.
    # By default it not used, can be extended from other addons.
    number_preprint = fields.Char(
        string='Preprint Number',
        copy=False,
    )

    @api.model
    def check_missing_tax(self):
        res = False  # Force not check missing tax
        return res

    @api.multi
    def action_number(self):
        result = super(AccountInvoice, self).action_number()
        self._compute_sales_tax_detail()
        self._check_tax_detail_info()  # Double checking
        self._assign_detail_tax_sequence()
        return result

    @api.multi
    def check_tax_lines(self, compute_taxes):
        """ This check tax detail as soon as it get created to speed up
        otherwise, it wait unitl move line created, it slow """
        self.ensure_one()
        res = super(AccountInvoice, self).check_tax_lines(compute_taxes)
        # Only check for case supplier invoice
        if self.type in ('in_refund', 'in_invoice'):
            self._check_tax_detail_info()
        return res

    @api.multi
    def action_cancel_draft(self):
        for rec in self:
            for invoice_tax in rec.tax_line:
                # Delete and recreate tax detail
                invoice_tax.detail_ids.unlink()
                if invoice_tax.tax_code_type == 'normal':
                    detail = invoice_tax._prepare_invoice_tax_detail()
                    self.env['account.tax.detail'].create(detail)
        res = super(AccountInvoice, self).action_cancel_draft()
        return res

    @api.multi
    def action_cancel(self):
        for rec in self:
            for line in rec.tax_line:
                line.detail_ids.write({'cancel': True})
        res = super(AccountInvoice, self).action_cancel()
        return res


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    detail_ids = fields.One2many(
        'account.tax.detail',
        'invoice_tax_id',
        string='Tax Detail',
    )

    @api.model
    def _prepare_invoice_tax_detail(self):
        currency = self.invoice_id.currency_id
        ttype = self.invoice_id.type
        doc_type = \
            ttype in ('out_invoice', 'out_refund') and 'sale' or 'purchase'
        return {'doc_type': doc_type,
                'currency_id': currency.id,
                'invoice_tax_id': self.id}

    @api.model
    def create(self, vals):
        invoice_tax = super(AccountInvoiceTax, self).create(vals)
        if invoice_tax.tax_code_type == 'normal':
            detail = invoice_tax._prepare_invoice_tax_detail()
            self.env['account.tax.detail'].create(detail)
        return invoice_tax

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
