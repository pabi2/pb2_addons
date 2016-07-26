# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError


class PaymentExportControl(models.Model):
    _name = 'payment.export.control'
    _description = 'Payment Export Control'

    name = fields.Char(
        string='Number',
        required=True,
        copy=False,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Payment Method',
        domain=[('type', '=', 'bank')],
        required=True,
    )
    bank_id = fields.Many2one(
        'res.partner.bank',
        string='Bank',
        compute='_compute_bank_id',
        store=True,
        required=True,
    )
    cheque_lot_id = fields.Many2one(
        'cheque.lot.control',
        string='Cheque Lot',
        domain="[('bank_id', '=', bank_id)]",
        required=True,
    )
    cheque_number_from = fields.Char(
        string='Cheque Number From',
        compute='_compute_cheque_number',
    )
    cheque_number_to = fields.Char(
        string='Cheque Number From',
        compute='_compute_cheque_number',
    )
    line_ids = fields.One2many(
        'payment.export.control.line',
        'control_id',
        string='Control Lines',
    )

    @api.one
    @api.depends('journal_id')
    def _compute_bank_id(self):
        Bank = self.env['res.partner.bank']
        bank = Bank.search([('journal_id', '=', self.journal_id.id)])
        if not bank:
            raise ValidationError(
                _('This Payment Method do not link to any Bank Account'))
        self.bank_id = bank


class PaymentExportControlLine(models.Model):
    _name = 'payment.export.control.line'
    _description = 'Payment Export Control Line'

    control_id = fields.Many2one(
        'payment.export.control',
        string='Payment Export Control',
        ondelete='cascade',
        index=True,
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        string='Supplier Payment',
        readonly=True,
    )
    amount = fields.Float(
        string='Amount',
        readonly=True,
    )
    cheque_number = fields.Char(
        string='Cheque Number',
        readonly=True,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('export', 'Exported'),
         ('cancel', 'Cancelled')],
        string='Status',
        required=True,
        default='draft',
    )
