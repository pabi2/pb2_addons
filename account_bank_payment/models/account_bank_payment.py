# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.exceptions import Warning as UserError


class AccountBankPayment(models.Model):
    _name = "account.bank.payment"
    _description = "Account Bank Payment"
    _order = 'payment_date desc'

    name = fields.Char(
        string='Name',
        size=64,
        readonly=True,
        default='',
        copy=False,
    )
    bank_intransit_ids = fields.One2many(
        'account.move.line',
        'bank_payment_id',
        string='Intransit Payments',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    payment_date = fields.Date(
        string='Payment Date', required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.context_today,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        domain=[('type', '=', 'bank'), ('purchase_intransit', '=', True)],
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Show only journal of type Bank & Cash "
             "and Purchase Bank Intransit = True",
    )
    journal_default_account_id = fields.Many2one(
        'account.account',
        related='journal_id.default_credit_account_id',
        string='Default Credit Account of the Journal',
        readonly=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    currency_none_same_company_id = fields.Many2one(
        'res.currency',
        compute='_compute_bank_payment',
        string='Currency (False if same as company)',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done'),
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
        readonly=True,
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
    )
    move_ids = fields.One2many(
        'account.move.line',
        related='move_id.line_id',
        string='Journal Items',
        readonly=True,
    )
    company_partner_id = fields.Many2one(
        'res.partner',
        string='Company Partner',
        related='company_id.partner_id',
        readonly=True,
    )
    partner_bank_id = fields.Many2one(
        'res.partner.bank',
        string='Bank Account',
        domain="['|', ('company_id', '=', company_id),"
               "('partner_id', '=', company_partner_id)]",
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    bank_account_id = fields.Many2one(
        'account.account',
        string="Bank's Account Code",
        related='partner_bank_id.journal_id.default_credit_account_id',
        readonly=True,
        help="Show credit account of Bank Account's Journal",
    )
    line_ids = fields.One2many(
        'account.move.line',
        related='move_id.line_id',
        string='Lines',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get(
            'account.bank.payment'),
    )
    total_amount = fields.Float(
        compute='_compute_bank_payment',
        string="Total Amount", readonly=True,
        digits=dp.get_precision('Account'),
    )
    intransit_count = fields.Integer(
        compute='_compute_bank_payment',
        readonly=True,
        string="Number of Intransit Payment",
    )
    is_reconcile = fields.Boolean(
        compute='_compute_bank_payment',
        readonly=True,
        string="Reconcile",
    )
    note = fields.Text(
        string='Notes',
    )
    validate_user_id = fields.Many2one(
        'res.users',
        string='Validated By',
        readonly=True,
        copy=False,
    )
    validate_date = fields.Date(
        'Validate On',
        readonly=True,
        copy=False,
    )

    @api.multi
    @api.depends('company_id', 'currency_id', 'bank_intransit_ids.credit',
                 'bank_intransit_ids.amount_currency',
                 'move_id.line_id.reconcile_id')
    def _compute_bank_payment(self):
        for payment in self:
            total = 0.0
            count = 0
            reconcile = False
            currency_none_same_company_id = False
            if payment.company_id.currency_id != payment.currency_id:
                currency_none_same_company_id = payment.currency_id.id
            for line in payment.bank_intransit_ids:
                count += 1
                if currency_none_same_company_id:
                    total += line.amount_currency
                else:
                    total += line.credit
            if payment.move_id:
                for line in payment.move_id.line_id:
                    if line.credit > 0 and line.reconcile_id:
                        reconcile = True
            payment.total_amount = total
            payment.is_reconcile = reconcile
            payment.currency_none_same_company_id =\
                currency_none_same_company_id
            payment.intransit_count = count

    @api.multi
    @api.constrains('currency_id', 'bank_intransit_ids', 'company_id')
    def _bank_payment(self):
        for payment in self:
            payment_currency = payment.currency_id
            if payment_currency == payment.company_id.currency_id:
                for line in payment.bank_intransit_ids:
                    if line.currency_id:
                        raise ValidationError(
                            _("The bank intransit with amount %s and "
                              "reference '%s' is in currency %s but the "
                              "payment is in currency %s.") % (
                                line.credit, line.ref or '',
                                line.currency_id.name,
                                payment_currency.name))
            else:
                for line in payment.bank_intransit_ids:
                    if line.currency_id != payment_currency:
                        raise ValidationError(
                            _("The bank intransit with amount %s and "
                              "reference '%s' is in currency %s but the "
                              "payment is in currency %s.") % (
                                line.credit, line.ref or '',
                                line.currency_id.name,
                                payment_currency.name))

    @api.multi
    def unlink(self):
        for payment in self:
            if payment.state == 'done':
                raise UserError(
                    _("The payment '%s' is in valid state, so you must "
                      "cancel it before deleting it.") % payment.name)
        return super(AccountBankPayment, self).unlink()

    @api.model
    def _cancel_move(self):
        # It will raise here if journal_id.update_posted = False
        self.move_id.button_cancel()
        for line in self.bank_intransit_ids:
            if line.reconcile_id:
                line.reconcile_id.unlink()
        self.move_id.unlink()

    @api.multi
    def cancel_bank_payment(self):
        for payment in self:
            if payment.move_id:
                payment._cancel_move()
            payment.write({'state': 'cancel'})

    @api.multi
    def backtodraft(self):
        for payment in self:
            payment.write({'state': 'draft'})
        return True

    @api.model
    def create(self, vals):
        # if vals.get('name', '/') == '/':
        #     vals['name'] = self.env['ir.sequence'].\
        #         next_by_code('account.bank.payment')
        vals['name'] = ''
        return super(AccountBankPayment, self).create(vals)

    @api.model
    def _prepare_account_move_vals(self, payment):
        date = payment.payment_date
        Period = self.env['account.period']
        period_ids = Period.find(dt=date)
        # period_ids will always have a value, cf the code of find()
        move_vals = {
            'journal_id': payment.journal_id.id,
            'date': date,
            'period_id': period_ids[0].id,
            'name': payment.name,
            'ref': payment.name,
        }
        return move_vals

    @api.model
    def _prepare_move_line_vals(self, line):
        assert (line.credit > 0), 'Credit must have a value'
        return {
            'name': _('Bank Intransit - Ref. %s') % line.ref,
            'credit': 0.0,
            'debit': line.credit,
            'account_id': line.account_id.id,
            'partner_id': line.partner_id.id,
            'currency_id': line.currency_id.id or False,
            'amount_currency': line.amount_currency * -1,
        }

    @api.model
    def _prepare_counterpart_move_lines_vals(
            self, payment, total_credit, total_amount_currency):
        return {
            'name': _('Bank Payment %s') % payment.name,
            'debit': 0.0,
            'credit': total_credit,
            'account_id': payment.bank_account_id.id,
            'partner_id': False,
            'currency_id': payment.currency_none_same_company_id.id or False,
            'amount_currency': total_amount_currency,
        }

    @api.model
    def _create_writeoff_move_line_hook(self, move):
        return True

    @api.model
    def _do_reconcile(self, to_reconcile_lines):
        for reconcile_lines in to_reconcile_lines:
            reconcile_lines.reconcile()
        return True

    @api.multi
    def validate_bank_payment(self):
        Move = self.env['account.move']
        MoveLine = self.env['account.move.line']
        for payment in self:
            # Check
            if not payment.bank_intransit_ids:
                raise UserError(_('No lines!'))
            if not payment.partner_bank_id:
                raise UserError(_("Missing Bank Account"))
            if not payment.bank_account_id:
                raise UserError(
                    _("Missing Account for Bank Payment on the journal '%s'.")
                    % payment.partner_bank_id.journal_id.name)

            # Create document number
            refer_type = 'bank_payment'
            doctype = payment.env['res.doctype'].get_doctype(refer_type)
            fiscalyear_id = payment.env['account.fiscalyear'].find()
            payment = payment.with_context(doctype_id=doctype.id,
                                           fiscalyear_id=fiscalyear_id)
            name = payment.env['ir.sequence'].next_by_code(
                'account.bank.payment')
            payment.write({'name': name})

            # --
            move_vals = self._prepare_account_move_vals(payment)
            move = Move.create(move_vals)
            total_credit = 0.0
            total_amount_currency = 0.0
            to_reconcile_lines = []
            for line in payment.bank_intransit_ids:
                total_credit += line.credit
                total_amount_currency += line.amount_currency
                line_vals = self._prepare_move_line_vals(line)
                line_vals['move_id'] = move.id
                move_line = MoveLine.create(line_vals)
                to_reconcile_lines.append(line + move_line)
            # Prepare for hook
            payment._create_writeoff_move_line_hook(move)
            # Create counter-part
            counter_vals = self._prepare_counterpart_move_lines_vals(
                payment, total_credit, total_amount_currency)
            counter_vals['move_id'] = move.id
            MoveLine.create(counter_vals)
            move.post()
            payment.write({'state': 'done',
                           'move_id': move.id,
                           'validate_user_id': self.env.user.id,
                           'validate_date': fields.Date.context_today(self),
                           })
            # We have to reconcile after post()
            payment._do_reconcile(to_reconcile_lines)
        return True

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id:
            partner_banks = self.env['res.partner.bank'].search(
                [('company_id', '=', self.company_id.id)])
            if len(partner_banks) == 1:
                self.partner_bank_id = partner_banks[0]
        else:
            self.partner_bank_id = False

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        self.bank_intransit_ids = False
        if self.journal_id:
            if self.journal_id.currency:
                self.currency_id = self.journal_id.currency
            else:
                self.currency_id = self.journal_id.company_id.currency_id
