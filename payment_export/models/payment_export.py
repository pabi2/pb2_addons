# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class PaymentExport(models.Model):
    _name = 'payment.export'
    _inherit = ['mail.thread']
    _description = 'Payment Export'

    name = fields.Char(
        string='Number',
        required=True,
        copy=False,
        readonly=True,
        default="/",
        size=500,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Payment Method',
        required=True,
        domain=[('type', '=', 'bank'), ('intransit', '=', False)],
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
    )
    partner_bank_id = fields.Many2one(
        'res.partner.bank',
        string='Bank Account',
        domain="[('partner_id', '=', company_partner_id)]",
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
        help="When Payment Method is selected, this field will default with "
        "bank account of type CA (current account)",
    )
    payment_type = fields.Selection(
        [('cheque', 'Cheque'),
         ('transfer', 'Transfer')],
        string='Payment Type',
        compute='_compute_payment_type',
        store=True,
    )
    transfer_type = fields.Selection(
        [('direct', 'DIRECT'),
         ('smart', 'SMART')
         ],
        string='Transfer Type',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="- DIRECT is transfer within same bank.\n"
        "- SMART is transfer is between different bank.",
        track_visibility='onchange',
    )
    # is_cheque_lot = fields.Boolean(
    #     string='Is Cheque Lot Available',
    #     compute='_compute_is_cheque_lot',
    # )
    cheque_lot_id = fields.Many2one(
        'cheque.lot',
        string='Cheque Lot',
        domain="[('journal_id', '=', journal_id), "
        "('state', '=', 'active')]",
        ondelete='restrict',
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
    )
    date_value = fields.Date(
        string='Value/Cheque Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
    )
    cheque_number_from = fields.Char(
        string='Cheque Number From',
        compute='_compute_cheque_number',
        track_visibility='onchange',
    )
    cheque_number_to = fields.Char(
        string='Cheque Number From',
        compute='_compute_cheque_number',
        track_visibility='onchange',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        required=True,
        readonly=True,
        default=lambda self: self.env.user,
        track_visibility='onchange',
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
        track_visibility='onchange',
    )
    cheque_register_id = fields.Many2one(
        'cheque.register',
        related='line_ids.cheque_register_id',
        string='Cheque Number',
        help='Search line for Cheque',
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        related='line_ids.voucher_id',
        string='Supplier Payment',
        help='Search line for Payment',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    company_partner_id = fields.Many2one(
        'res.partner',
        string='Company Partner',
        related='company_id.partner_id',
        readonly=True,
    )
    sum_amount = fields.Float(
        compute="_compute_sum_amount",
        string="Sum Amount",
        store=True,
        copy=False,
    )
    sum_total = fields.Float(
        compute="_compute_sum_amount",
        string="Sum Total",
        store=True,
        copy=False,
    )
    num_line = fields.Integer(
        compute="_compute_num_line",
        string="Num Lines",
        store=True,
    )
    cancel_reason_txt = fields.Char(
        string="Description",
        readonly=True,
        size=500,
    )
    exported = fields.Boolean(
        string='Pack Exported',
        default=False,
        help="Only if exported pack, will allow printing Payment Export",
    )
    line_filter = fields.Char(
        string='Filter',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="More filter. You can use complex search with comma and between.",
    )
    attachment_ids = fields.One2many(
        'ir.attachment',
        'res_id',
        string='Attachment',
        copy=False,
        domain=[('res_model', '=', 'payment.export')],
    )

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        self.partner_bank_id = False
        if self.journal_id:
            BankAcct = self.env['res.partner.bank']
            banks = BankAcct.search([('journal_id', '=', self.journal_id.id),
                                     ('state', '=', 'CA')])
            self.partner_bank_id = banks and banks[0] or False

    @api.multi
    def _assign_line_sequence(self):
        for export in self:
            i = 1
            for line in export.line_ids:
                line.write({'sequence': i})
                i += 1

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('payment.export') or '/'
        export = super(PaymentExport, self).create(vals)
        export._assign_line_sequence()
        return export

    @api.multi
    def write(self, vals):
        res = super(PaymentExport, self).write(vals)
        if 'line_ids' in vals:
            self._assign_line_sequence()
        # Write export id back to voucher
        if vals.get('state') == 'done':
            for export in self:
                # Write back the export id
                export.line_ids.mapped('voucher_id').\
                    write({'payment_export_id': export.id})
        return res

    @api.onchange('transfer_type')
    def _onchange_transfer_type(self):
        if self.transfer_type:
            self.cheque_lot_id = False

    @api.onchange('cheque_lot_id')
    def _onchange_cheque_lot_id(self):
        if self.cheque_lot_id:
            self.transfer_type = False

    @api.depends('line_ids',
                 'line_ids.amount',
                 'line_ids.amount_total')
    def _compute_sum_amount(self):
        for export in self:
            export.sum_amount = sum(export.line_ids.mapped('amount'))
            export.sum_total = sum(export.line_ids.mapped('amount_total'))

    @api.multi
    @api.depends('line_ids')
    def _compute_num_line(self):
        for export in self:
            export.num_line = len(export.line_ids)

    @api.multi
    def _compute_cheque_number(self):
        for export in self:
            self._cr.execute("""
                select min(cr.number) min, max(cr.number) max
                from payment_export_line pel
                join cheque_register cr on cr.id = pel.cheque_register_id
                where pel.export_id = %s
            """, (export.id,))
            res = self._cr.fetchone()
            export.cheque_number_from = res[0]
            export.cheque_number_to = res[1]

    @api.multi
    @api.depends('transfer_type', 'cheque_lot_id')
    def _compute_payment_type(self):
        for rec in self:
            if rec.transfer_type:
                rec.payment_type = 'transfer'
            elif rec.cheque_lot_id:
                rec.payment_type = 'cheque'
            else:
                rec.payment_type = False

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        self.cheque_lot_id = False

    @api.onchange('journal_id', 'cheque_lot_id',
                  'date_value', 'transfer_type',
                  'line_filter')
    def _onchange_compute_payment_export_line(self):
        self.line_ids = False
        self.line_ids = []
        if not (self.journal_id and self.date_value):  # At least
            return
        if not self.transfer_type and not self.cheque_lot_id:
            return
        Voucher = self.env['account.voucher']
        # Prepare voucher domain
        dom = [('journal_id', '=', self.journal_id.id),
               ('date_value', '=', self.date_value),
               ('state', '=', 'posted')]
        if self.transfer_type:
            dom.append(('transfer_type', '=', self.transfer_type))
        if self.line_filter:
            dom.append(('number', 'ilike', self.line_filter))
        # Prepare export lines
        ExportLine = self.env['payment.export.line']
        # Case Cheque, make sure it has not been in any valid cheque before
        # if self.is_cheque_lot:
        if self.cheque_lot_id:
            chequed_voucher_ids = [x.voucher_id.id
                                   for x in self.cheque_lot_id.line_ids
                                   if x.voucher_id and not x.void]
            dom.append(('cheque_lot_id', '=', self.cheque_lot_id.id))
            dom.append(('id', 'not in', chequed_voucher_ids))
        # else:
        elif self.transfer_type:  # Export case, has not been exported before
            lines = ExportLine.search(
                [('export_id.state', '=', 'done'),
                 ('export_id.date_value', '=', self.date_value)],
            )
            exported_voucher_ids = [x.voucher_id.id for x in lines]
            dom.append(('id', 'not in', exported_voucher_ids))
        vouchers = Voucher.search(dom, order='id',
                                  limit=self.cheque_lot_id.remaining)
        for voucher in vouchers:
            export_line = ExportLine.new()
            export_line.voucher_id = voucher
            export_line.amount = voucher.amount
            self.line_ids += export_line

    @api.multi
    def action_export_payment_pack(self):
        raise ValidationError(_('No implementation for the export function!'))

    @api.multi
    def action_assign_cheque_number(self):
        # if not self.is_cheque_lot:
        if not self.cheque_lot_id:
            return
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
        for export in self:
            if not export.line_ids:
                raise ValidationError(_('No Export Lines'))
            # Check Supplier Payment
            export._check_payment_export_line()
            voucher_ids = [x.voucher_id.id for x in export.line_ids]
            exported_lines = self.env['payment.export.line'].\
                search([('voucher_id', 'in', voucher_ids),
                        ('export_id.state', '=', 'done'),
                        ('void', '=', False)])
            if exported_lines:
                vouchers = [x.voucher_id.number for x in exported_lines]
                message = _('Following payment had been exported.\n%s\nPlease '
                            'remove to continue.') % (', '.join(vouchers),)
                raise ValidationError(message)
            # Case Cheque only
            # if export.is_cheque_lot and export.cheque_lot_id:
            if export.cheque_lot_id:
                for line in export.line_ids:
                    if not line.cheque_register_id:
                        raise ValidationError(
                            _('Some Payments is not assigned with Cheque '
                              'Number!\nPlease click Assign Cheque Number.'
                              ))
                    if line.cheque_register_id.voucher_id:
                        raise ValidationError(
                            _('Cheque Number %s is occupied, \
                                please reassign again!')
                            % (line.cheque_register_id.number))
                    if line.cheque_register_id.void:
                        raise ValidationError(
                            _('Cheque Number %s is voided, please reassign'
                              ' again!')
                            % (line.cheque_register_id.number))
                    line.cheque_register_id.write(
                        {'voucher_id': line.voucher_id.id,
                         'payment_export_id': export.id}
                    )
                    cheque_register = line.cheque_register_id
                    cheque_number = cheque_register.number
                    cheque_date = export.date_value
                    # bank account
                    bank = export.partner_bank_id
                    bank_name = bank and bank.name_get() and \
                        bank.display_name
                    bank_branch = bank and bank.bank_branch.name_get() and \
                        bank.bank_branch.display_name
                    # --
                    line.voucher_id.write({
                        'date_cheque': cheque_date,
                        'number_cheque': cheque_number,
                        'bank_cheque': bank_name,
                        'bank_branch': bank_branch,
                    })
                    line.write({'exported': True})
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self, void_cheque=False):
        self.write({'state': 'cancel'})
        for rec in self:
            for line in rec.line_ids:
                vals = {'voucher_id': False,
                        'payment_export_id': False,
                        }
                if void_cheque:
                    vals.update({'void': True,
                                 'note': rec.cancel_reason_txt})
                # delete number_cheque
                voucher = line.cheque_register_id.voucher_id
                voucher.write({'number_cheque': False,
                               'payment_export_id': False, })
                # Delete infor in cheque.register
                line.cheque_register_id.write(vals)
                line.write({'exported': False})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def _check_payment_export_line(self):
        self.ensure_one()
        for line in self.line_ids:
            if line.voucher_id.state != 'posted':
                raise ValidationError(
                    _('Some export line is not valid, please refresh '
                      'by changing payment method or transfer type.'))


class PaymentExportLine(models.Model):
    _name = 'payment.export.line'
    _description = 'Payment Export Line'

    sequence = fields.Integer(
        string='Sequence',
        readonly=True,
    )
    export_id = fields.Many2one(
        'payment.export',
        string='Payment Export',
        ondelete='cascade',
        index=True,
    )
    payment_type = fields.Selection(
        [('cheque', 'Cheque'),
         ('transfer', 'Transfer')],
        string='Payment Type',
        related='export_id.payment_type',
        store=True,
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
    invoice_source_documents = fields.Char(
        string='Source Documents',
        related='voucher_id.invoice_source_documents',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        related='voucher_id.partner_id',
        string='Supplier',
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
    amount_fee = fields.Float(
        string="Fee",
        copy=False,
    )
    amount_total = fields.Float(
        compute="_compute_total",
        string="Total",
        store=True,
        copy=False,
    )
    nstda_fee = fields.Boolean(
        string='NSTDA Fee',
    )

    @api.depends('amount', 'amount_fee')
    def _compute_total(self):
        for line in self:
            line.amount_total = line.amount + line.amount_fee
