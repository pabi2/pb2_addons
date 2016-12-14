# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.exceptions import Warning as UserError


class AccountBankReceipt(models.Model):
    _name = "account.bank.receipt"
    _description = "Account Bank Receipt"
    _order = 'receipt_date desc'

    name = fields.Char(
        string='Name',
        size=64,
        readonly=True,
        default='/',
    )
    bank_intransit_ids = fields.One2many(
        'account.move.line',
        'bank_receipt_id',
        string='Intransit Payments',
        states={'done': [('readonly', '=', True)]},
    )
    receipt_date = fields.Date(
        string='Receipt Date', required=True,
        states={'done': [('readonly', '=', True)]},
        default=fields.Date.context_today,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        domain=[('type', '=', 'bank'), ('intransit', '=', True)],
        required=True,
        states={'done': [('readonly', '=', True)]},
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
        states={'done': [('readonly', '=', True)]},
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
        states={'done': [('readonly', '=', True)]},
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
        states={'done': [('readonly', '=', True)]},
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
                raise UserError(
                    _("The receipt '%s' is in valid state, so you must "
                      "cancel it before deleting it.") % receipt.name)
        return super(AccountBankReceipt, self).unlink()

    @api.multi
    def cancel_bank_receipt(self):
        for receipt in self:
            if receipt.move_id:
                # It will raise here if journal_id.update_posted = False
                receipt.move_id.button_cancel()
                for line in receipt.bank_intransit_ids:
                    if line.reconcile_id:
                        line.reconcile_id.unlink()
                receipt.move_id.unlink()
            receipt.write({'state': 'cancel'})

    @api.multi
    def backtodraft(self):
        for receipt in self:
            receipt.write({'state': 'draft'})
        return True

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].\
                next_by_code('account.bank.receipt')
        return super(AccountBankReceipt, self).create(vals)

    @api.model
    def _prepare_account_move_vals(self, receipt):
        date = receipt.receipt_date
        period_obj = self.env['account.period']
        period_ids = period_obj.find(dt=date)
        # period_ids will always have a value, cf the code of find()
        move_vals = {
            'journal_id': receipt.journal_id.id,
            'date': date,
            'period_id': period_ids[0].id,
            'name': _('Bank Receipt %s') % receipt.name,
            'ref': receipt.name,
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

    @api.multi
    def validate_bank_receipt(self):
        am_obj = self.env['account.move']
        aml_obj = self.env['account.move.line']
        for receipt in self:
            move_vals = self._prepare_account_move_vals(receipt)
            move = am_obj.create(move_vals)
            total_debit = 0.0
            total_amount_currency = 0.0
            to_reconcile_lines = []
            for line in receipt.bank_intransit_ids:
                total_debit += line.debit
                total_amount_currency += line.amount_currency
                line_vals = self._prepare_move_line_vals(line)
                line_vals['move_id'] = move.id
                move_line = aml_obj.create(line_vals)
                to_reconcile_lines.append(line + move_line)

            # Create counter-part
            if not receipt.partner_bank_id:
                raise UserError(_("Missing Bank Account"))
            if not receipt.bank_account_id:
                raise UserError(
                    _("Missing Account for Bank Receipt on the journal '%s'.")
                    % receipt.partner_bank_id.journal_id.name)

            counter_vals = self._prepare_counterpart_move_lines_vals(
                receipt, total_debit, total_amount_currency)
            counter_vals['move_id'] = move.id
            aml_obj.create(counter_vals)

            move.post()
            receipt.write({'state': 'done', 'move_id': move.id})
            # We have to reconcile after post()
            for reconcile_lines in to_reconcile_lines:
                reconcile_lines.reconcile()
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
        if self.journal_id:
            if self.journal_id.currency:
                self.currency_id = self.journal_id.currency
            else:
                self.currency_id = self.journal_id.company_id.currency_id


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    bank_receipt_id = fields.Many2one(
        'account.bank.receipt', string='Bank Receipt', copy=False)
