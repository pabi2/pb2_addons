# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError


class AccountBankReceipt(models.Model):
    _name = "account.bank.receipt"
    _description = "Account Bank Receipt"
    _order = 'receipt_date desc'

    name = fields.Char(
        string='Name',
        size=64,
        readonly=True,
        # default='/',
        copy=False,
    )
    bank_intransit_ids = fields.One2many(
        'account.move.line',
        'bank_receipt_id',
        string='Intransit Payments',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    receipt_date = fields.Date(
        string='Receipt Date', required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.context_today,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        domain=[('type', 'in', ('bank', 'cash')), ('intransit', '=', True)],
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Show only journal of type Bank & Cash and Bank Intransit = True",
    )
    journal_default_account_id = fields.Many2one(
        'account.account',
        related='journal_id.default_debit_account_id',
        string='Default Debit Account of the Journal',
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
        compute='_compute_bank_receipt',
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
        related='partner_bank_id.journal_id.default_debit_account_id',
        readonly=True,
        help="Show debit account of Bank Account's Journal",
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
            'account.bank.receipt'),
    )
    total_amount = fields.Float(
        compute='_compute_bank_receipt',
        string="Total Amount", readonly=True,
        digits=dp.get_precision('Account'),
    )
    intransit_count = fields.Integer(
        compute='_compute_bank_receipt',
        readonly=True,
        string="Number of Intransit Payment",
    )
    is_reconcile = fields.Boolean(
        compute='_compute_bank_receipt',
        readonly=True,
        string="Reconcile",
    )
    note = fields.Text(
        string='Notes',
        size=1000,
    )
    validate_user_id = fields.Many2one(
        'res.users',
        string='Validated By',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
    )
    validate_date = fields.Date(
        'Validate On',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
    )
    line_filter = fields.Char(
        string='Filter',
        readonly=True,
        states={'draft': [('readonly', False)]},
        size=500,
        help="More filter. You can use complex search with comma and between.",
    )

    @api.multi
    @api.depends('company_id', 'currency_id', 'bank_intransit_ids.debit',
                 'bank_intransit_ids.amount_currency',
                 'move_id.line_id.reconcile_id')
    def _compute_bank_receipt(self):
        for receipt in self:
            total = 0.0
            count = 0
            reconcile = False
            currency_none_same_company_id = False
            if receipt.company_id.currency_id != receipt.currency_id:
                currency_none_same_company_id = receipt.currency_id.id
            for line in receipt.bank_intransit_ids:
                count += 1
                if currency_none_same_company_id:
                    total += line.amount_currency
                else:
                    total += line.debit
            if receipt.move_id:
                for line in receipt.move_id.line_id:
                    if line.debit > 0 and line.reconcile_id:
                        reconcile = True
            receipt.total_amount = total
            receipt.is_reconcile = reconcile
            receipt.currency_none_same_company_id =\
                currency_none_same_company_id
            receipt.intransit_count = count

    @api.multi
    @api.constrains('currency_id', 'bank_intransit_ids', 'company_id')
    def _bank_receipt(self):
        for receipt in self:
            receipt_currency = receipt.currency_id
            if receipt_currency == receipt.company_id.currency_id:
                for line in receipt.bank_intransit_ids:
                    if line.currency_id:
                        raise ValidationError(
                            _("The bank intransit with amount %s and "
                              "reference '%s' is in currency %s but the "
                              "receipt is in currency %s.") % (
                                line.debit, line.ref or '',
                                line.currency_id.name,
                                receipt_currency.name))
            else:
                for line in receipt.bank_intransit_ids:
                    if line.currency_id != receipt_currency:
                        raise ValidationError(
                            _("The bank intransit with amount %s and "
                              "reference '%s' is in currency %s but the "
                              "receipt is in currency %s.") % (
                                line.debit, line.ref or '',
                                line.currency_id.name,
                                receipt_currency.name))

    @api.multi
    def unlink(self):
        for receipt in self:
            if receipt.state == 'done':
                raise ValidationError(
                    _("The receipt '%s' is in valid state, so you must "
                      "cancel it before deleting it.") % receipt.name)
        return super(AccountBankReceipt, self).unlink()

    @api.model
    def _cancel_move(self):
        # It will raise here if journal_id.update_posted = False
        self.move_id.button_cancel()
        for line in self.bank_intransit_ids:
            if line.reconcile_id:
                line.reconcile_id.unlink()
        self.move_id.unlink()

    @api.multi
    def cancel_bank_receipt(self):
        for receipt in self:
            if receipt.move_id:
                receipt._cancel_move()
            receipt.write({'state': 'cancel'})

    @api.multi
    def backtodraft(self):
        for receipt in self:
            receipt.write({'state': 'draft'})
        return True

    # @api.model
    # def create(self, vals):
    #     if vals.get('name', '/') == '/':
    #         vals['name'] = self.env['ir.sequence'].\
    #             next_by_code('account.bank.receipt')
    #     return super(AccountBankReceipt, self).create(vals)

    @api.model
    def _prepare_account_move_vals(self, receipt):
        # Validate
        bank = receipt.partner_bank_id
        if not bank.journal_id:
            raise ValidationError(_('Bank Account has no Account Journal!'))
        date = receipt.receipt_date
        Period = self.env['account.period']
        period_ids = Period.find(dt=date)
        # period_ids will always have a value, cf the code of find()
        number = self.env['ir.sequence'].next_by_code('account.bank.receipt')
        move_vals = {
            'journal_id': bank.journal_id.id,
            'date': date,
            'period_id': period_ids[0].id,
            'name': number,
            'ref': number,
        }
        return move_vals

    @api.model
    def _prepare_move_line_vals(self, line):
        assert (line.debit > 0), 'Debit must have a value'
        return {
            'name': _('Bank Intransit - Ref. %s') % line.ref,
            'credit': line.debit,
            'debit': 0.0,
            'account_id': line.account_id.id,
            'partner_id': line.partner_id.id,
            'currency_id': line.currency_id.id or False,
            'amount_currency': line.amount_currency * -1,
        }

    @api.model
    def _prepare_counterpart_move_lines_vals(
            self, receipt, total_debit, total_amount_currency):
        return {
            'name': _('Bank Receipt %s') % receipt.name,
            'debit': total_debit,
            'credit': 0.0,
            'account_id': receipt.bank_account_id.id,
            'partner_id': False,
            'currency_id': receipt.currency_none_same_company_id.id or False,
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
    def validate_bank_receipt(self):
        Move = self.env['account.move']
        MoveLine = self.env['account.move.line']
        for receipt in self:
            # Check
            if not receipt.bank_intransit_ids:
                raise ValidationError(_('No lines!'))
            if not receipt.partner_bank_id:
                raise ValidationError(_("Missing Bank Account"))
            if not receipt.bank_account_id:
                raise ValidationError(
                    _("Missing Account for Bank Receipt on the journal '%s'.")
                    % receipt.partner_bank_id.journal_id.name)
            # --
            move_vals = self._prepare_account_move_vals(receipt)
            move = Move.create(move_vals)
            total_debit = 0.0
            total_amount_currency = 0.0
            to_reconcile_lines = []
            for line in receipt.bank_intransit_ids:
                total_debit += line.debit
                total_amount_currency += line.amount_currency
                line_vals = self._prepare_move_line_vals(line)
                line_vals['move_id'] = move.id
                move_line = MoveLine.create(line_vals)
                to_reconcile_lines.append(line + move_line)
            # Prepare for hook
            receipt._create_writeoff_move_line_hook(move)
            # Create counter-part
            counter_vals = self._prepare_counterpart_move_lines_vals(
                receipt, total_debit, total_amount_currency)
            counter_vals['move_id'] = move.id
            MoveLine.create(counter_vals)
            if move.state != 'posted':
                move.post()
            receipt.write({'name': move.name,
                           'state': 'done',
                           'move_id': move.id,
                           'validate_user_id': self.env.user.id,
                           'validate_date': fields.Date.context_today(self),
                           })
            # We have to reconcile after post()
            receipt._do_reconcile(to_reconcile_lines)
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

    @api.onchange('line_filter')
    def _onchange_line_filter(self):
        # Base domain
        domain = [('reconcile_id', '=', False),
                  ('debit', '>', 0),
                  ('currency_id', '=', self.currency_none_same_company_id.id),
                  ('journal_id', '=', self.journal_id.id),
                  ('account_id', '=', self.journal_default_account_id.id)]
        if self.line_filter:
            # Must be ilike to use extended search
            domain.append(('ref', 'ilike', self.line_filter))
            move_lines = self.env['account.move.line'].search(domain)
            self.bank_intransit_ids |= move_lines
