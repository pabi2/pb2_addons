# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    intransit = fields.Boolean(
        string='Bank Intransit',
        related='journal_id.intransit',
        readonly=True,
    )
    bank_receipt_id = fields.Many2one(
        'account.bank.receipt',
        string='Bank Receipt',
        related='move_id.bank_receipt_id',
        readonly=True,
    )
