# -*- coding: utf-8 -*-

from openerp import models, api


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

    @api.model
    def move_line_get(self, invoice_id):
        res = super(AccountInvoiceTax, self).move_line_get(invoice_id)
        invoice = self.env['account.invoice'].browse(invoice_id)
        if invoice.partner_id.property_tax_move_by_taxbranch:
            for r in res:
                r.update({'taxbranch_id': invoice.taxbranch_id.id})
        return res
