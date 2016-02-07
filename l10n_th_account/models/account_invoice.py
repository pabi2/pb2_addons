# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm


class account_invoice(models.Model):

    _inherit = 'account.invoice'

    amount_retention = fields.Float(
        string='Retention',
        digits=dp.get_precision('Account'),
        readonly=False)
    retention_on_payment = fields.Boolean(
        string='Retention on Payment',
        compute='_retention_on_payment',
        store=True,
        help="If checked, retention will done during payment")

    @api.one
    @api.depends('invoice_line.price_subtotal',
                 'tax_line.amount',
                 'amount_retention')
    def _compute_amount(self):
        super(account_invoice, self)._compute_amount()
        self.amount_tax = sum(line.amount
                              for line in self.tax_line
                              if not line.is_wht)  # WHT
        amount_total = self.amount_untaxed + self.amount_tax
        if not self.retention_on_payment:
            self.amount_total = amount_total - self.amount_retention  # RET
        else:
            self.amount_total = amount_total

    @api.one
    @api.depends('partner_id')
    def _retention_on_payment(self):
        self.retention_on_payment = \
            self.partner_id.property_retention_on_payment

    @api.multi
    def invoice_pay_customer(self):
        res = super(account_invoice, self).invoice_pay_customer()
        if res:
            res['context']['default_amount'] = 0.0
        return res


class account_invoice_line(models.Model):

    _inherit = "account.invoice.line"

    @api.model
    def move_line_get(self, invoice_id):

        res = super(account_invoice_line, self).move_line_get(invoice_id)
        inv = self.env['account.invoice'].browse(invoice_id)

        if inv.amount_retention > 0.0 and not inv.retention_on_payment:
            sign = -1
            # sign = inv.type in ('out_invoice','in_invoice') and -1 or 1
            # account code for advance
            prop = inv.type in ('out_invoice', 'out_refund') \
                and self.env['ir.property'].get(
                    'property_account_retention_customer',
                    'res.partner') \
                or self.env['ir.property'].get(
                    'property_account_retention_supplier',
                    'res.partner')
            if not prop:
                raise except_orm(
                    _('Error!'),
                    _('No retention account defined in the system!'))
            account = self.env['account.fiscal.position'].map_account(prop)
            res.append({
                'type': 'src',
                'name': _('Retention Amount'),
                'price_unit': sign * inv.amount_retention,
                'quantity': 1,
                'price': sign * inv.amount_retention,
                'account_id': account.id,
                'product_id': False,
                'uos_id': False,
                'account_analytic_id': False,
                'taxes': False,
            })
        return res


class account_invoice_tax(models.Model):

    _inherit = 'account.invoice.tax'

    is_wht = fields.Boolean(
        string="Withholding Tax",
        readonly=True,
        default=False,
        help="Tax will be withhold and will be used in Payment")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
