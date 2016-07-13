# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def check_missing_tax(self):
        res = False  # Force not check missing tax
        return res

    @api.multi
    def action_move_create(self):
        for invoice in self:
            for tax in invoice.tax_line:
                for detail in tax.detail_ids:
                    if (not detail.partner_id or
                            not detail.invoice_number or
                            not detail.invoice_date):
                        raise UserError(
                            _('Some data in Tax Detail is not filled!'))
        result = super(AccountInvoice, self).action_move_create()
        return result


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    detail_ids = fields.One2many(
        'account.invoice.tax.detail',
        'invoice_tax_id',
        string='Tax Detail',
    )

    @api.model
    def create(self, vals):
        invoice_tax = super(AccountInvoiceTax, self).create(vals)
        detail = {'invoice_tax_id': invoice_tax.id}
        self.env['account.invoice.tax.detail'].create(detail)
        return invoice_tax


class AccountInvoiceTaxDetail(models.Model):
    _name = 'account.invoice.tax.detail'

    invoice_tax_id = fields.Many2one(
        'account.invoice.tax',
        ondelete='cascade',
        index=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    invoice_number = fields.Char(
        string='Tax Invoice Number',
    )
    invoice_date = fields.Date(
        string='Invoice Date',
    )
    base = fields.Float(
        string='Base',
    )
    amount = fields.Float(
        string='Tax',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
