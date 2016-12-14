# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountBankReceipt(models.Model):
    _inherit = 'account.bank.receipt'

    cancel_move_id = fields.Many2one(
        'account.move',
        string='Cancel Journal Entry',
        readonly=True,
        index=True,
        ondelete='restrict',
        copy=False,
    )

    # TODO: add cancellation option for Bank Receipt
