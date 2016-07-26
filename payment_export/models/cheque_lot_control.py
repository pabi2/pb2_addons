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
    current_number = fields.Integer(
        string='Current Number',
    )
    state = fields.Selection(
        [('active', 'Active'),
         ('inactive', 'Inactive')],
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
