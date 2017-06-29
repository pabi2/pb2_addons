# -*- coding: utf-8 -*-
import datetime
from openerp import api, models, fields


class AccountTaxWizard(models.TransientModel):
    _name = "account.tax.wizard"

    invoice_tax_id = fields.Many2one(
        'account.invoice.tax',
        string='Invoice Tax',
        readonly=True,
    )
    voucher_tax_id = fields.Many2one(
        'account.voucher.tax',
        string='Voucher Tax',
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
        'account.tax.detail.wizard',
        'wizard_id',
        string='Tax Details',
    )
    is_readonly = fields.Boolean(
        string='Readonly',
    )

    @api.model
    def default_get(self, fields):
        res = super(AccountTaxWizard, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        tax = self.env[active_model].browse(active_id)
        doc = False
        date_doc = False
        if active_model == 'account.invoice.tax':
            res['invoice_tax_id'] = tax.id
            doc = tax.invoice_id
            date_doc = doc.date_invoice
            res['is_readonly'] = doc.state != 'draft'
        else:
            res['voucher_tax_id'] = tax.id
            doc = tax.voucher_id
            if doc.auto_recognize_vat:
                res['is_readonly'] = doc.state != 'draft'
            elif doc.recognize_vat_move_id:
                res['is_readonly'] = True
        res['base'] = tax.base
        res['amount'] = tax.amount
        res['detail_ids'] = []
        # For refund, show negative number
        sign = doc.journal_id.type in ('sale_refund', 'purchase_refund') \
            and -1 or 1
        for line in tax.detail_ids:
            partner = line.partner_id or doc.partner_id
            vals = {
                'tax_detail_id': line.id,
                'period_id': line.period_id.id,
                'partner_id': partner.id,
                'vat': partner.vat,
                'taxbranch': partner.taxbranch,
                'invoice_date': (line.invoice_date or
                                 date_doc or
                                 False),
                'base': line.base or (sign * tax.base) or False,
                'amount': line.amount or (sign * tax.amount) or False,
                'tax_sequence': line.tax_sequence,
                'addition': line.addition,
            }
            if active_model == 'account.invoice.tax':
                if doc.type in ('in_invoice', 'in_refund'):
                    vals['invoice_number'] = (line.invoice_number or
                                              False)
            else:
                if doc.type in ('payment'):
                    vals['invoice_number'] = (line.invoice_number or False)
            res['detail_ids'].append((0, 0, vals))
        return res

    @api.multi
    def save_tax_detail(self):
        self.ensure_one()
        active_model = self._context.get('active_model')
        # if active_model == 'account.invoice.tax':
        #     self.invoice_tax_id.detail_ids.unlink()
        # elif active_model == 'account.voucher.tax':
        #     self.voucher_tax_id.detail_ids.unlink()
        doc = False
        date_doc = False
        line_tax = False
        if active_model == 'account.invoice.tax':
            doc = self.invoice_tax_id.invoice_id
            date_doc = doc.date_invoice
            line_tax = self.invoice_tax_id
        elif active_model == 'account.voucher.tax':
            doc = self.voucher_tax_id.voucher_id
            date_doc = doc.date
            line_tax = self.voucher_tax_id
        InvoiceTax = self.env['account.invoice.tax']
        TaxDetail = self.env['account.tax.detail']
        for line in self.detail_ids:
            doc_type = doc.type in ('out_invoice', 'out_refund', 'receipt') \
                and 'sale' or 'purchase'
            vals = TaxDetail._prepare_tax_detail(self.invoice_tax_id.id,
                                                 self.voucher_tax_id.id,
                                                 doc_type,
                                                 line.partner_id.id,
                                                 line.invoice_number,
                                                 line.invoice_date,
                                                 line.base, line.amount)
            if line.tax_detail_id:
                line.tax_detail_id.write(vals)
            else:
                TaxDetail.create(vals)
        # Update overall base / amount
        sum_base = sum([x.base for x in self.detail_ids])
        sum_amount = sum([x.amount for x in self.detail_ids])
        base_amount = InvoiceTax.base_change(sum_base,
                                             doc.currency_id.id,
                                             doc.company_id.id,
                                             date_doc,
                                             )['value']['base_amount']
        tax_amount = InvoiceTax.amount_change(sum_amount,
                                              doc.currency_id.id,
                                              doc.company_id.id,
                                              date_doc,
                                              )['value']['tax_amount']
        # use abs() when write to cover refund case when wizard show (-)
        line_tax.write({'base': abs(sum_base),
                        'amount': abs(sum_amount),
                        'base_amount': abs(base_amount),
                        'tax_amount': abs(tax_amount),
                        })
        # Update Supplier Invoice Number
        if active_model == 'account.invoice.tax':
            numbers = list(set([x.invoice_number
                                for x in self.detail_ids if x.invoice_number]))
            if numbers:
                doc.write({'supplier_invoice_number': ', '.join(numbers)})
        return True


class AccountInvoiceTaxDetailWizard(models.TransientModel):
    _name = "account.tax.detail.wizard"

    wizard_id = fields.Many2one(
        'account.tax.wizard',
        string='Wizard',
        ondelete='cascade',
        index=True,
        required=True,
    )
    tax_detail_id = fields.Many2one(
        'account.tax.detail',
        string='Tax Detail',
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
    )
    vat = fields.Char(
        string='Tax ID',
        readonly=True,
    )
    vat_readonly = fields.Char(
        string='Tax ID',
        related='vat',
    )
    taxbranch = fields.Char(
        string='Tax Branch ID',
        readonly=True,
    )
    taxbranch_readonly = fields.Char(
        string='Tax Branch ID',
        related='taxbranch',
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
    tax_sequence = fields.Integer(
        string='Sequence',
        readonly=True,
        help="Running sequence for the same period. Reset every period",
    )
    tax_sequence_display = fields.Char(
        string='Sequence',
        compute='_compute_tax_sequence_display',
    )
    addition = fields.Boolean(
        string='Past Period Tax',
        default=False,
        readonly=True,
    )
    is_readonly = fields.Boolean(
        related='wizard_id.is_readonly',
        string='Readonly',
    )

    @api.multi
    @api.depends('tax_sequence')
    def _compute_tax_sequence_display(self):
        for rec in self:
            if rec.period_id and rec.tax_sequence:
                date_start = rec.period_id.date_start
                mo = datetime.datetime.strptime(date_start,
                                                '%Y-%m-%d').date().month
                month = '{:02d}'.format(mo)
                sequence = '{:04d}'.format(rec.tax_sequence)
                rec.tax_sequence_display = '%s/%s' % (month, sequence)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.vat = self.partner_id.vat
        self.taxbranch = self.partner_id.taxbranch
