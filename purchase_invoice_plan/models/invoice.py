# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    is_deposit_invoice = fields.Boolean(
        string='Deposit Invoice',
    )
    copy_invoice_id = fields.Many2one(
        'account.invoice',
        string="Invoice Copy",
        readonly=True,
    )
