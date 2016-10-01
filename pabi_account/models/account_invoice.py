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

    show_account = fields.Boolean(
        string='Show account (hide product)',
        default=False,
        change_default=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    invoice_line_show_account = fields.One2many(
        'account.invoice.line',
        'invoice_id',
        string='Invoice Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=True,
        help="Used when user choose option Show Account instead of Product"
    )

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(AccountInvoice, self).line_get_convert(line, part, date)
        res.update({
            'taxbranch_id': line.get('taxbranch_id', False),
        })
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def onchange_account_id(self, product_id, partner_id, inv_type,
                            fposition_id, account_id):
        res = super(AccountInvoiceLine, self).onchange_account_id(
            product_id, partner_id, inv_type, fposition_id, account_id)
        account = self.env['account.account'].browse(account_id)
        if not res.get('value'):
            res['value'] = {}
        res['value'].update({'name': account.name})
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
        tax_move_by_taxbranch = self.env.user.company_id.tax_move_by_taxbranch
        if tax_move_by_taxbranch:
            invoice = self.env['account.invoice'].browse(invoice_id)
            for r in res:
                r.update({'taxbranch_id': invoice.taxbranch_id.id})
        return res
