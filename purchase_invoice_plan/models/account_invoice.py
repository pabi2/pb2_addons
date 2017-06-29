# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    invoice_plan_ids = fields.One2many(
        'purchase.invoice.plan',
        'ref_invoice_id',
        string='Invoice Plan',
        copy=False,
        readonly=True,
    )
