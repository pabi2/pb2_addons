# -*- coding: utf-8 -*-

from openerp import models, fields


class SaleInvoicePlan(models.Model):
    _inherit = "sale.invoice.plan"

    date_paid = fields.Date(
        string='Paid Date',
        related='ref_invoice_id.date_paid'
    )
    payment_ids = fields.Many2many(
        'account.move.line',
        string='Payments',
        related='ref_invoice_id.payment_ids'
    )
