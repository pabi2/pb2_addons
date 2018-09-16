# -*- coding: utf-8 -*-

from openerp import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    cancel_reason_txt = fields.Char(
        string="Description",
        readonly=True,
        size=500,
    )
