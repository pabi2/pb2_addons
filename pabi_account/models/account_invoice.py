# -*- coding: utf-8 -*-

from openerp import models, api, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    validate_user_id = fields.Many2one(
        'res.users',
        string='Validated By',
        readonly=True,
        copy=False,
    )
    validate_date = fields.Date(
        'Validate On',
        readonly=True,
        copy=False,
    )

    @api.multi
    def invoice_validate(self):
        result = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            invoice.write({'validate_user_id': self.env.user.id,
                           'validate_date': fields.Date.today()})
        return result

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
