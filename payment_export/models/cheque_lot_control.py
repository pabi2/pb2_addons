# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class ChequeLotControl(models.Model):
    _name = 'cheque.lot.control'
    _description = 'Cheque Lot Control'
    _order = 'id desc'

    name = fields.Char(
        string='Number',
        required=True,
        copy=False,
    )
    bank_id = fields.Many2one(
        'res.partner.bank',
        string='Bank',
    )
    cheque_number_from = fields.Char(
        string='Cheque Number From',
        size=10,
        required=True,
    )
    cheque_number_to = fields.Char(
        string='Cheque Number To',
        size=10,
        required=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        required=True,
    )
    next_number = fields.Char(
        string='Next Cheque Number',
        size=10,
        compute='_compute_next_number',
    )
    state = fields.Selection(
        [('active', 'Active'),
         ('inactive', 'Inactive'),
         ],
        string='Status',
    )

    @api.multi
    @api.constrains('cheque_number_from', 'cheque_number_to')
    def _compute_cheque_number(self):
        for rec in self:
            if not rec.cheque_number_from.isdigit() or \
                    not rec.cheque_number_to.isdigit():
                raise ValidationError(
                    _('Cheque Number must not contain any character!'))
            if int(rec.cheque_number_from) >= int(rec.cheque_number_to):
                raise ValidationError(
                    _('Cheque Number From - To must be a valid number range!'))
            if len(rec.cheque_number_from) != len(rec.cheque_number_to):
                raise ValidationError(
                    _('Cheque Number From - To must be in same digit length!'))

    @api.multi
    @api.depends()
    def _compute_next_number(self):
        for rec in self:
            rec.next_number = '10000001'


class ChequeRegistration(models.Model):
    _name = 'cheque.registration'
    _description = 'Cheque Registration'
    _rec = 'number'
    _order = 'number'

    cheque_lot_id = fields.Many2one(
        'cheque.lot.control',
        string='Cheque Lot Control',
        ondelete='cascade',
        index=True,
    )
    bank_id = fields.Many2one(
        'res.partner.bank',
        string='Bank Account',
        related='cheque_lot_id.bank_id',
        store=True,
    )
    number = fields.Char(
        string='Cheque Number',
        size=10,
        readonly=True,
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        string='Supplier Payment',
        readonly=True,
    )
    amount = fields.Float(
        string='Amount',
        related='voucher_id.amount',
        readonly=True,
    )
