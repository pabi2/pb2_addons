# -*- coding: utf-8 -*-
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    amount_retention = fields.Float(
        string='Retention',
        readonly=True,
        compute='_compute_amount',
        digits=dp.get_precision('Account'),
        store=True,
    )
    percent_retention = fields.Float(
        string='Percent Retention',
        readonly=True,
    )
    retention_type = fields.Selection(
        [('before_vat', 'Before VAT'),
         ('after_vat', 'After VAT')],
        string='Type',
        readonly=True,
    )

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount',
                 'percent_retention')
    def _compute_amount(self):
        super(AccountInvoice, self)._compute_amount()
        if self.percent_retention and self.retention_type:
            amount_retention = 0.0
            # Amount without advance deduction
            amount_before_vat = sum([(l.price_subtotal > 0.0 and
                                      l.price_subtotal or 0.0) for
                                     l in self.invoice_line])
            if self.retention_type == 'before_vat':
                amount_retention = (amount_before_vat *
                                    self.percent_retention / 100)
            if self.retention_type == 'after_vat':
                amount_tax = 0.0
                for l in self.invoice_line:
                    taxes = l.invoice_line_tax_id.compute_all(
                        (l.price_unit * (1 - (l.discount or 0.0) / 100.0)),
                        l.quantity, l.product_id, self.partner_id)['taxes']
                    amount_tax += sum(tax['amount'] > 0.0 and
                                      tax['amount'] or 0.0 for
                                      tax in taxes)
                amount_after_vat = (amount_before_vat + amount_tax)
                amount_retention = (amount_after_vat *
                                    self.percent_retention / 100)
            self.amount_retention = amount_retention
            if not self.retention_on_payment:
                self.amount_total = (self.amount_untaxed +
                                     self.amount_tax - amount_retention)
