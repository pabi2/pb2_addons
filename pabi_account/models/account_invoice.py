# -*- coding: utf-8 -*-

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(AccountInvoice, self).line_get_convert(line, part, date)
        res.update({
            'taxbranch_id': line.get('taxbranch_id', False),
        })
        return res


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        related='invoice_id.taxbranch_id',
        string='Tax Branch',
        readonly=True,
        store=True,
    )

    @api.model
    def _prepare_invoice_tax_detail(self, invoice_tax):
        res = super(AccountInvoiceTax, self).\
            _prepare_invoice_tax_detail(invoice_tax)
        res.update({'taxbranch_id': invoice_tax.invoice_id.taxbranch_id.id})
        return res

    @api.model
    def move_line_get(self, invoice_id):
        res = super(AccountInvoiceTax, self).move_line_get(invoice_id)
        invoice = self.env['account.invoice'].browse(invoice_id)
        if invoice.partner_id.property_tax_move_by_taxbranch:
            for r in res:
                r.update({'taxbranch_id': invoice.taxbranch_id.id})
        return res
