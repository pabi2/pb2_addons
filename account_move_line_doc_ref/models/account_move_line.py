# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    doc_ref = fields.Char(
        string='Doc Ref',
        copy=True,  # True for cancel reversal case
    )
    doc_id = fields.Reference(
        [('account.invoice', 'Invoice'),
         ('account.move', 'Journal Entry'),
         ('account.voucher', 'Voucher'),
         ('account.asset.asset', 'Asset'),
         ('account.bank.receipt', 'Bank Receipt'),
         ('stock.picking', 'Picking')],
        string='Doc Ref',
        readonly=True,
        copy=True,  # True for cancel reversal case
    )
