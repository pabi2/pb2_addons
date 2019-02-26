# -*- coding: utf-8 -*-
from datetime import datetime
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from pychart.arrow import default



class ChequeLot(models.Model):
    _name = 'cheque.lot'
    _inherit = ['mail.thread']
    _description = 'Cheque Lot'
    _order = 'id desc'

    name = fields.Char(
        string='Lot',
        required=True,
        copy=False,
        track_visibility='onchange',
        size=500,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Payment Method',
        required=True,
        domain=[('type', '=', 'bank'), ('intransit', '=', False)],
        track_visibility='onchange',
    )
    cheque_number_from = fields.Char(
        string='Cheque Number From',
        size=10,
        required=True,
        track_visibility='onchange',
    )
    cheque_number_to = fields.Char(
        string='Cheque Number To',
        size=10,
        required=True,
        track_visibility='onchange',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        required=False,
        readonly=False,
        track_visibility='onchange',
    )
    next_number = fields.Char(
        string='Next Cheque Number',
        size=10,
        compute='_compute_next_number',
    )
    remaining = fields.Integer(
        string='Remainings',
        compute='_compute_remaining',
        readonly=True,
        store=True,
        help="This field show the remaining valid cheque to use",
    )
    voided = fields.Integer(
        string='Voided',
        compute='_compute_voided',
        help="This field show the voided cheque",
    )
    dirty = fields.Boolean(
        string='Dirty',
        compute='_compute_remaining',
        help="Dirty remaining is not equal to number of lines"
    )
    state = fields.Selection(
        [('active', 'Active'),
         ('inactive', 'Inactive'),
         ],
        string='Status',
        compute='_compute_state',
        store=True,
        readonly=True,
        help="Active means this lot is in used.\n"
        "Inactive means this lot has been used up.\n"
        "But if no Responsible selected, always Inactive",
        track_visibility='onchange',
    )
    line_ids = fields.One2many(
        'cheque.register',
        'cheque_lot_id',
        string='Cheque Registers',
    )    

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.line_ids.filtered('voucher_id'):
                raise ValidationError(
                    _('This lot has been used, deletion no allowed!'))
        return super(ChequeLot, self).unlink()

    # @api.onchange('bank_id')
    # def _onchange_bank_id(self):
    #     self.journal_id = False

    @api.multi
    @api.depends('line_ids', 'line_ids.void', 'line_ids.voucher_id')
    def _compute_remaining(self):
        Cheque = self.env['cheque.register']
        for lot in self:
            count = len(Cheque.search([('cheque_lot_id', '=', lot.id),
                                      ('voucher_id', '=', False),
                                      ('void', '!=', True)])._ids)
            lot.remaining = count
            lot.dirty = lot.remaining != len(lot.line_ids)

    @api.multi
    def _compute_voided(self):
        for lot in self:
            lot.voided = len(lot.line_ids.filtered('void').ids)

    @api.multi
    @api.depends('user_id', 'line_ids', 'line_ids.void', 'line_ids.voucher_id')
    def _compute_state(self):
        for lot in self:
            # No responsible, always inactive
            if not lot.user_id:
                lot.state = 'inactive'
                continue
            # With responsible, inactive if completed.
            if lot.remaining > 0:
                lot.state = 'active'
            else:
                lot.state = 'inactive'

    @api.multi
    @api.constrains('dirty', 'user_id')
    def _check_user_id(self):
        for rec in self:
            if rec.dirty and not rec.user_id:
                raise ValidationError(
                    _('Responsible is required as this lot is dirty.'))

    @api.multi
    @api.constrains('cheque_number_from', 'cheque_number_to')
    def _check_cheque_number(self):
        for rec in self:
            # Check number only
            if not rec.cheque_number_from.isdigit() or \
                    not rec.cheque_number_to.isdigit():
                raise ValidationError(
                    _('Cheque Number must not contain any character!'))
            # Check valid range
            if int(rec.cheque_number_from) >= int(rec.cheque_number_to):
                raise ValidationError(
                    _('Cheque Number From - To must be a valid number range!'))
            # Check number length
            SystemParam = self.env['ir.config_parameter']
            length = SystemParam.get_param('cheque_lot_number_length') or 8
            length = length.isdigit() and int(length) or 8
            if len(rec.cheque_number_from) != int(length) or \
                    len(rec.cheque_number_to) != length:
                raise ValidationError(
                    _('Cheque Number From - To must has %s digit!') %
                    (length,))
            # Check same number length
            if len(rec.cheque_number_from) != len(rec.cheque_number_to):
                raise ValidationError(
                    _('Cheque Number From - To must be in same digit length!'))

    @api.multi
    def _compute_next_number(self):
        for rec in self:
            self._cr.execute("""
                select min(number) from cheque_register
                where cheque_lot_id = %s
                and voucher_id is null
                and void = false
            """, (rec.id,))
            rec.next_number = self._cr.fetchone()[0] or False

    @api.multi
    def _generate_cheque_register(self):
        ChequeRegister = self.env['cheque.register']
        for rec in self:
            a = int(rec.cheque_number_from)
            b = int(rec.cheque_number_to) + 1
            if (b - a) > 1000:  # Not allow > 1000 cheques
                raise ValidationError(
                    _('Creating more than 1,000 number is not allowed!'))
            padding = len(rec.cheque_number_from)
            for i in range(a, b):
                cheque_number = str(i).zfill(padding)
                ChequeRegister.create({'cheque_lot_id': rec.id,
                                       'number': cheque_number})

    @api.model
    def create(self, vals):
        cheque_lot = super(ChequeLot, self).create(vals)
        cheque_lot._generate_cheque_register()
        return cheque_lot

    @api.multi
    def write(self, vals):
        res = super(ChequeLot, self).write(vals)
        for cheque_lot in self:
            if 'cheque_number_from' in vals or 'cheque_number_to' in vals:
                if cheque_lot.line_ids.filtered(lambda l:  # if any is used.
                                                l.voucher_id or l.void):
                    raise ValidationError(
                        _('Renumbering is not allowed, some lines used!'))
                else:
                    cheque_lot.line_ids.unlink()
                    cheque_lot._generate_cheque_register()
        return res

    @api.multi
    def open_cheque_register(self):
        self.ensure_one()
        action = self.env.ref('payment_export.action_cheque_register')
        result = action.read()[0]
        dom = [('cheque_lot_id', '=', self.id)]
        result.update({'domain': dom})
        return result

    @api.model
    def get_draft_cheque_register_range(self, cheque_lot_id, limit):
        self._cr.execute("""
            select id from cheque_register
            where cheque_lot_id = %s
            and voucher_id is null
            and void = false
            order by number
            limit %s
        """, (cheque_lot_id, limit,))
        res = [x[0] for x in self._cr.fetchall()]
        if len(res) < limit:
            raise ValidationError(_('Not enough draft Cheque on this lot'))
        return res


class ChequeRegister(models.Model):
    _name = 'cheque.register'
    _description = 'Cheque Register'
    _rec_name = 'number'
    _order = 'number'

    number = fields.Char(
        string='Cheque Number',
        size=10,
        readonly=True,
    )
    cheque_lot_id = fields.Many2one(
        'cheque.lot',
        string='Cheque Lot',
        ondelete='cascade',
        readonly=True,
        index=True,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Payment Method',
        related='cheque_lot_id.journal_id',
        store=True,
        readonly=True,
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        string='Supplier Payment',
        readonly=True,
    )
    posting_date = fields.Date(
        related='voucher_id.date',
        string='Posting Date',
        readonly=True,
    )
    period = fields.Many2one(
        related='voucher_id.period_id',
        string='Period',
        readonly=True,
    )
    amount = fields.Float(
        string='Amount',
        related='voucher_id.amount',
        readonly=True,
    )
    void = fields.Boolean(
        string='Void',
        default=False,
    )
    note = fields.Text(
        string='Cancellation Reasons',
        size=1000,
    )
    payment_export_id = fields.Many2one(
        'payment.export',
        string='Payment Export',
        readonly=True,
    )
    date_void = fields.Datetime(
        string='Voided Date',
        readonly=True,
    )
    _sql_constraints = [
        ('number_unique',
         'unique(number, journal_id)',
         'Cheque number must be unique of the same payment method!')
    ]   
    user_id = fields.Char(
        related='cheque_lot_id.user_id.name',
        string='Update by',
    )   
    update_date = fields.Date(
        compute='_compute_write_date',
        string='Update date'
    )
          
    @api.depends('payment_export_id')
    def _compute_write_date(self):
        for record in self:
            if record.payment_export_id.write_date :
                record.update_date = datetime.strptime(record.payment_export_id.write_date,'%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d")

    @api.multi
    def write(self, vals):
        if 'void' in vals:
            if vals['void']:
                now = fields.Datetime.context_timestamp(self, datetime.now())
                self.write({'date_void': now})
            else:
                self.write({'date_void': False})
        return super(ChequeRegister, self).write(vals)
