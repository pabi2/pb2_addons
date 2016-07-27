# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError, Warning as UserError


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
    date_value = fields.Date(
        string='Value/Cheque Date',
        required=True,
    )
    bank_id = fields.Many2one(
        'res.partner.bank',
        string='Bank Account',
        compute='_compute_bank_cheque_lot',
    )
    is_cheque_lot = fields.Boolean(
        string='Is Cheque Lot Available',
        compute='_compute_bank_cheque_lot',
    )
    cheque_lot_id = fields.Many2one(
        'cheque.lot.control',
        string='Cheque Lot',
        domain="[('bank_id', '=', bank_id), ('state', '=', 'active')]",
        ondelete='restrict',
    )
    cheque_number_from = fields.Char(
        string='Cheque Number From',
        # compute='_compute_cheque_number',
    )
    cheque_number_to = fields.Char(
        string='Cheque Number From',
        # compute='_compute_cheque_number',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        required=True,
        default=lambda self: self._uid,
    )
    line_ids = fields.One2many(
        'payment.export.control.line',
        'control_id',
        string='Control Lines',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done'),
         ('cancel', 'Cancelled'),
         ],
        string='Status',
        default='draft',
        required=True,
    )

    @api.one
    @api.depends('journal_id')
    def _compute_bank_cheque_lot(self):
        Bank = self.env['res.partner.bank']
        if not self.journal_id:
            self.bank_id = False
            self.is_cheque_lot = False
            return
        bank = Bank.search([('journal_id', '=', self.journal_id.id)])
        if bank:
            self.bank_id = bank
            if bank.lot_control_ids:
                self.is_cheque_lot = True
        else:
            self.bank_id = False
            self.is_cheque_lot = False

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        self.cheque_lot_id = False

    @api.onchange('journal_id', 'cheque_lot_id', 'date_value')
    def _onchange_compute_payment_export_line(self):
        self.line_ids = []
        if not self.journal_id or not self.date_value:  # At least
            return
        if self.is_cheque_lot and not self.cheque_lot_id:  # Case Lot
            return
        Voucher = self.env['account.voucher']
        ControlLine = self.env['payment.export.control.line']
        dom = [('journal_id', '=', self.journal_id.id),
               ('date_value', '=', self.date_value),
               ('state', '=', 'posted')]
        if self.is_cheque_lot:
            dom.append(('cheque_lot_id', '=', self.cheque_lot_id.id))
        vouchers = Voucher.search(dom)
        for voucher in vouchers:
            control_line = ControlLine.new()
            control_line.voucher_id = voucher
            control_line.amount = voucher.amount
            self.line_ids += control_line

    @api.multi
    def action_assign_cheque_number(self):
        for rec in self:
            
            first_number = rec.next_number
            if not first_number:
                raise UserError(_('No draft Cheque available on this lot'))
            for line in rec.line_ids:
                

class PaymentExportControlLine(models.Model):
    _name = 'payment.export.control.line'
    _description = 'Payment Export Control Line'

    control_id = fields.Many2one(
        'payment.export.control',
        string='Payment Export Control',
        ondelete='cascade',
        index=True,
    )
    cheque_number = fields.Char(
        string='Cheque Number',
        readonly=True,
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
    state = fields.Selection(
        [('draft', 'Draft'),
         ('export', 'Exported'),
         ('cancel', 'Cancelled')],
        string='Status',
        required=True,
        default='draft',
    )
