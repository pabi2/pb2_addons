# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, Warning as UserError


class PaymentExport(models.Model):
    _name = 'payment.export'
    _description = 'Payment Export'

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
        'cheque.lot',
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
        'payment.export.line',
        'export_id',
        string='Payment Export Lines',
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
            if bank.lot_ids:
                self.is_cheque_lot = True
        else:
            self.bank_id = False
            self.is_cheque_lot = False

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        self.cheque_lot_id = False

    @api.onchange('journal_id', 'cheque_lot_id', 'date_value')
    def _onchange_compute_payment_export_line(self):
        self.line_ids = False
        self.line_ids = []
        if not self.journal_id or not self.date_value:  # At least
            return
        if self.is_cheque_lot and not self.cheque_lot_id:  # Case Lot
            return
        Voucher = self.env['account.voucher']
        ExportLine = self.env['payment.export.line']
        dom = [('journal_id', '=', self.journal_id.id),
               ('date_value', '=', self.date_value),
               ('state', '=', 'posted')]
        if self.is_cheque_lot:
            printed_voucher_ids = [x.voucher_id.id
                                   for x in self.cheque_lot_id.line_ids
                                   if x.voucher_id and not x.void]
            dom.append(('cheque_lot_id', '=', self.cheque_lot_id.id))
            dom.append(('id', 'not in', printed_voucher_ids))
        vouchers = Voucher.search(dom, order='date desc',
                                  limit=self.cheque_lot_id.remaining)
        for voucher in vouchers:
            export_line = ExportLine.new()
            export_line.voucher_id = voucher
            export_line.amount = voucher.amount
            self.line_ids += export_line

    @api.multi
    def action_assign_cheque_number(self):
        ChequeLot = self.env['cheque.lot']
        for rec in self:
            limit = len(rec.line_ids)
            cheque_lot_id = rec.cheque_lot_id.id
            res = ChequeLot.get_draft_cheque_register_range(cheque_lot_id,
                                                            limit)
            for i in range(limit):
                rec.line_ids[i].cheque_register_id = res[i]

    @api.multi
    def action_done(self):
        for rec in self:
            rec.line_ids.write({'exported': True})
            for line in rec.line_ids:
                if not line.cheque_register_id:
                    raise UserError(
                        _('Some Payments is not assigned with Cheque Number!\n'
                          'Please click Assign Cheque Number.'))
                if line.cheque_register_id.voucher_id:
                    raise UserError(
                        _('Cheque Number %s is occupied, please reassign '
                          'again!') % (line.cheque_register_id.number))
                if line.cheque_register_id.void:
                    raise UserError(
                        _('Cheque Number %s is voided, please reassign '
                          'again!') % (line.cheque_register_id.number))
                line.cheque_register_id.voucher_id = line.voucher_id
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})
        for rec in self:
            rec.line_ids.write({'exported': False})
            for line in rec.line_ids:
                line.cheque_register_id.voucher_id = False

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})


class PaymentExportLine(models.Model):
    _name = 'payment.export.line'
    _description = 'Payment Export Line'

    export_id = fields.Many2one(
        'payment.export',
        string='Payment Export',
        ondelete='cascade',
        index=True,
    )
    cheque_register_id = fields.Many2one(
        'cheque.register',
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
    void = fields.Boolean(
        string='Void',
        related='cheque_register_id.void',
        readonly=True,
    )
    exported = fields.Boolean(
        string='Exported',
        default=False,
    )
