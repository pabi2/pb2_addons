# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    amount_retention = fields.Float(
        string='Retention',
        digits=dp.get_precision('Account'),
        readonly=False,
    )
    retention_on_payment = fields.Boolean(
        string='Retention on Payment',
        compute='_retention_on_payment',
        store=True,
        help="If checked, retention will done during payment",
    )
    move_ids = fields.One2many(
        'account.move.line',
        related='move_id.line_id',
        string='Journal Items',
        readonly=True,
    )
    date_paid = fields.Date(
        string='Paid Date',
        compute='_compute_date_paid',
        store=True,
    )

    @api.multi
    @api.depends('state')
    def _compute_date_paid(self):
        for rec in self:
            if rec.state == 'paid' and rec.payment_ids:
                rec.date_paid = max(rec.payment_ids.mapped('date'))
            elif rec.state == 'open':
                rec.date_paid = False

    @api.one
    @api.depends('invoice_line.price_subtotal',
                 'tax_line.amount',
                 'amount_retention')
    def _compute_amount(self):
        super(AccountInvoice, self)._compute_amount()
        self.amount_tax = sum(line.amount
                              for line in self.tax_line)
        amount_total = self.amount_untaxed + self.amount_tax
        if not self.retention_on_payment:
            self.amount_total = amount_total - self.amount_retention  # RET
        else:
            self.amount_total = amount_total

    @api.one
    @api.depends('partner_id')
    def _retention_on_payment(self):
        self.retention_on_payment = \
            self.env.user.company_id.retention_on_payment

    @api.multi
    def invoice_pay_customer(self):
        res = super(AccountInvoice, self).invoice_pay_customer()
        if res:
            res['context']['default_amount'] = 0.0
        return res


class AccountInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    @api.model
    def move_line_get(self, invoice_id):

        res = super(AccountInvoiceLine, self).move_line_get(invoice_id)
        inv = self.env['account.invoice'].browse(invoice_id)

        if inv.amount_retention > 0.0 and not inv.retention_on_payment:
            sign = -1
            # sign = inv.type in ('out_invoice','in_invoice') and -1 or 1
            account_id = False
            company = self.env.user.company_id
            if inv.type in ('out_invoice', 'out_refund'):
                account_id = company.account_retention_customer.id
            else:
                account_id = company.account_retention_supplier.id
            res.append({
                'type': 'src',
                'name': _('Retention Amount'),
                'price_unit': sign * inv.amount_retention,
                'quantity': 1,
                'price': sign * inv.amount_retention,
                'account_id': account_id,
                'product_id': False,
                'uos_id': False,
                'account_analytic_id': False,
                'taxes': False,
            })
        return res


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    tax_code_type = fields.Selection(
        [('normal', 'Normal'),
         ('undue', 'Undue'),
         ('wht', 'Withholding')],
        string='Tax Code Type',
        related='tax_code_id.tax_code_type',
        store=True,
        help="Type based on Tax using this Tax Code",
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
