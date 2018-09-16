# -*- coding: utf-8 -*-

from openerp import models, fields


class AccountBankReceipt(models.Model):
    _inherit = 'account.bank.receipt'

    cancel_reason_txt = fields.Char(
        string="Description",
        readonly=True,
        size=500,
    )
