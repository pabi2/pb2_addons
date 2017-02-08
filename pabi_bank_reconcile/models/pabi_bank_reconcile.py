# -*- coding: utf-8 -*-
from openerp import fields, models


class PABIBankReconcile(models.TransientModel):
    _name = 'pabi.bank.reconcile'

    name = fields.Char(
        string='Name',
        default='/',
        required=True,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Payment Method',
    )
    payment_type = fields.Selection(
        [('cheque', 'Cheque'),
         ('transfer', 'Transfer')],
        string='Payment Type',
    )
    transfer_type = fields.Selection(
        [('direct', 'DIRECT'),
         ('smart', 'SMART')],
        string='Transfer Type',
    )
    date_from = fields.Date(
        string'From Date',
    )
    date_to = fields.Date(
        string'To Date',
    )
    line_ids = fields.One2many(
        'reconcile_id',
        'pabi.bank.reconcile.line'
        string='Reconcile Lines',
    )


class PABIBankReconcileLine(models.TransientModel):
    _name = 'pabi.bank.reconcile.line'

    reconcile_id = fields.Many2one(
        'pabi.bank.reconcile',
        string='Reconcile ID',
        index=True,
        ondelete='cascade',
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        string='Payment Voucher',
    )
    cheque_number = fields.Char(
        string='Cheque',
        related='voucher_id.number_cheque',
        store=True,
    )
    amount = fields.Float(
        string='Amount',
        relatd='voucher_id.amount',
        store=True,
    )
    bank_cheque_number = fields.Char(
        string='Cheque'
    )
    bank_amount = fields.Float(
        string='Amount',
    )
