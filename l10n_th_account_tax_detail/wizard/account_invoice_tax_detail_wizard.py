# -*- coding: utf-8 -*-
from openerp import api, models, fields


class AccountInvoiceTaxWizard(models.TransientModel):
    _name = "account.invoice.tax.wizard"

    invoice_tax_id = fields.Many2one(
        'account.invoice.tax',
        string='Invoice Tax',
        readonly=True,
    )
    base = fields.Float(
        string='Base',
        readonly=True,
    )
    amount = fields.Float(
        string='Tax',
        readonly=True,
    )
    detail_ids = fields.One2many(
        'account.invoice.tax.detail.wizard',
        'wizard_id',
        string='Tax Details',
    )
    is_readonly = fields.Boolean(
        string='Readonly',
    )

    @api.model
    def default_get(self, fields):
        res = super(AccountInvoiceTaxWizard, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        invoice_tax = self.env[active_model].browse(active_id)
        invoice = invoice_tax.invoice_id
        res['invoice_tax_id'] = invoice_tax.id
        res['base'] = invoice_tax.base
        res['amount'] = invoice_tax.amount
        res['is_readonly'] = invoice.state != 'draft'
        res['detail_ids'] = []
        for line in invoice_tax.detail_ids:
            vals = {
                'tax_detail_id': line.id,
                'partner_id': line.partner_id.id or invoice.partner_id.id,
                'invoice_date': (line.invoice_date or
                                 invoice.date_invoice or
                                 False),
                'base': line.base or invoice_tax.base or False,
                'amount': line.amount or invoice_tax.amount or False,
            }
            # Supplier Invoice only, invoice number is manually keyed
            if invoice.type in ('in_invoice', 'in_refund'):
                vals['invoice_number'] = (line.invoice_number or
                                          invoice.supplier_invoice_number or
                                          False)
            res['detail_ids'].append((0, 0, vals))
        return res

    @api.multi
    def save_tax_detail(self):
        self.ensure_one()
        self.invoice_tax_id.detail_ids.unlink()
        invoice = self.invoice_tax_id.invoice_id
        InvoiceTax = self.env['account.invoice.tax']
        TaxDetail = self.env['account.invoice.tax.detail']
        for line in self.detail_ids:
            vals = {
                'invoice_tax_id': self.invoice_tax_id.id,
                'partner_id': line.partner_id.id,
                'invoice_number': line.invoice_number,
                'invoice_date': line.invoice_date,
                'base': line.base,
                'amount': line.amount,
            }
            if line.tax_detail_id:
                line.tax_detail_id.write(vals)
            else:
                TaxDetail.create(vals)
        # Update overall base / amount
        sum_base = sum([x.base for x in self.detail_ids])
        sum_amount = sum([x.amount for x in self.detail_ids])
        base_amount = InvoiceTax.base_change(sum_base,
                                             invoice.currency_id.id,
                                             invoice.company_id.id,
                                             invoice.date_invoice,
                                             )['value']['base_amount']
        tax_amount = InvoiceTax.amount_change(sum_amount,
                                              invoice.currency_id.id,
                                              invoice.company_id.id,
                                              invoice.date_invoice,
                                              )['value']['tax_amount']
        self.invoice_tax_id.write({'base': sum_base,
                                   'amount': sum_amount,
                                   'base_amount': base_amount,
                                   'tax_amount': tax_amount,
                                   })
        return True


class AccountInvoiceTaxDetailWizard(models.TransientModel):
    _name = "account.invoice.tax.detail.wizard"

    wizard_id = fields.Many2one(
        'account.invoice.tax.wizard',
        string='Wizard',
        ondelete='cascade',
        index=True,
        required=True,
    )
    tax_detail_id = fields.Many2one(
        'account.invoice.tax.detail',
        string='Tax Detail',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
    )
    invoice_number = fields.Char(
        string='Tax Invoice Number',
        required=True,
    )
    invoice_date = fields.Date(
        string='Invoice Date',
        required=True,
    )
    base = fields.Float(
        string='Base',
        required=True,
    )
    amount = fields.Float(
        string='Tax',
        required=True,
    )
