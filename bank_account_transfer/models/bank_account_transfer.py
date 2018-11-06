# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError


class BankAccountTransfer(models.Model):
    _name = 'bank.account.transfer'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Name',
        size=64,
        readonly=True,
        default='',
        copy=False,
    )
    transfer_line_ids = fields.One2many(
        'bank.account.transfer.line',
        'bank_transfer_id',
        string='Transfer Line',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date = fields.Date(
        string='Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
    )
    from_account_id = fields.Many2one(
        'account.account',
        string='From Account',
        domain="[('type', '=', 'liquidity')]",
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
    )
    to_account_id = fields.Many2one(
        'account.account',
        string='To Account',
        domain="[('type', '=', 'liquidity')]",
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
    )
    fee_account_id = fields.Many2one(
        'account.account',
        string='Fee Account',
        domain="[('type', '!=', 'view')]",
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    note = fields.Text(
        string='Notes',
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done'),
         ('cancel', 'Cancel')],
        string='Status',
        default='draft',
        readonly=True,
        track_visibility='onchange',
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        default=lambda self: self._get_journal(),
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        readonly=True,
        default=lambda self: self.env.user.company_id.currency_id,
        track_visibility='onchange',
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        copy=False,
        track_visibility='onchange',
    )
    deduct_account_id = fields.Many2one(
        'account.account',
        string='Deduct From',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    move_ids = fields.One2many(
        'account.move.line',
        related='move_id.line_id',
        string='Journal Items',
        readonly=True,
    )
    amount_transfer = fields.Float(
        string='Transfer Amount',
        compute='_compute_transfer_amount',
        readonly=True,
    )
    amount_fee = fields.Float(
        string='Fee',
        compute='_compute_fee',
        readonly=True,
    )
    amount_total = fields.Float(
        string='Total',
        compute='_compute_amount_total',
        readonly=True,
    )

    @api.model
    def _get_journal(self):
        return self.env.ref(
            'bank_account_transfer.journal_bank_transfer', False)

    @api.multi
    def _compute_transfer_amount(self):
        for rec in self:
            rec.amount_transfer = sum(
                rec.transfer_line_ids.mapped('transfer_amount'))

    @api.multi
    def _compute_fee(self):
        for rec in self:
            rec.amount_fee = sum(
                rec.transfer_line_ids.mapped('fee'))

    @api.multi
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = rec.amount_transfer + rec.amount_fee

    @api.model
    def _prepare_account_move_vals(self, transfer):
        date = transfer.date
        Period = self.env['account.period']
        period_ids = Period.find(dt=date)
        name = transfer.env['ir.sequence'].next_by_doctype()
        move_vals = {
            'journal_id': transfer.journal_id.id,
            'period_id': period_ids[0].id,
            'name': name,
            'ref': name,
        }
        return move_vals

    @api.model
    def _prepare_credit_line_vals(self, company_amount, company_currency):
        assert (company_amount > 0), 'Credit must have a value'
        return {
            'name': _('Bank Transfer'),
            'credit': company_amount,
            'debit': 0.0,
            'account_id': self.from_account_id.id,
            'currency_id':
                self.currency_id.id
                if company_currency != self.currency_id else False,
        }

    @api.model
    def _prepare_dedit_line_vals(self, company_amount, company_currency):
        assert (company_amount > 0), 'Credit must have a value'
        return {
            'name': _('Bank Transfer'),
            'credit': 0.0,
            'debit': company_amount,
            'account_id': self.to_account_id.id,
            'currency_id':
                self.currency_id.id
                if company_currency != self.currency_id else False,
        }

    @api.model
    def _prepare_fee_credit_move_lines_vals(
            self, company_fee, company_currency):
        return {
            'name': _('Bank Fee'),
            'debit': 0.0,
            'credit': company_fee,
            'account_id': self.deduct_account_id.id,
            'currency_id':
                self.currency_id.id
                if company_currency != self.currency_id else False,
        }

    @api.model
    def _prepare_fee_debit_move_lines_vals(
            self, company_fee, company_currency):
        return {
            'name': _('Bank Fee'),
            'debit': company_fee,
            'credit': 0.0,
            'account_id': self.fee_account_id.id,
            'currency_id':
                self.currency_id.id
                if company_currency != self.currency_id else False,
        }

    @api.multi
    def action_bank_transfer(self):
        Move = self.env['account.move']
        MoveLine = self.env['account.move.line']
        company_currency = self.env.user.company_id.currency_id
        for transfer in self:
            if transfer.fee_account_id and not transfer.deduct_account_id:
                raise ValidationError(_('Please fill deduct from.'))
            if not transfer.transfer_line_ids:
                raise ValidationError(_('No lines!'))
            if transfer.from_account_id == transfer.to_account_id:
                raise ValidationError(_('From Account and To Account \
                                can not be the same account. Please Change!!'))
            if sum(transfer.transfer_line_ids.mapped('fee')) and \
                    not transfer.fee_account_id:
                raise ValidationError(_('No Fee Account!'))

            refer_type = 'bank_transfer'
            doctype = transfer.env['res.doctype'].get_doctype(refer_type)
            fiscalyear_id = transfer.env['account.fiscalyear'].find()
            transfer = transfer.with_context(doctype_id=doctype.id,
                                             fiscalyear_id=fiscalyear_id)
            move_vals = self._prepare_account_move_vals(transfer)
            move = Move.create(move_vals)
            trans_currency = transfer.currency_id
            for line in transfer.transfer_line_ids:
                company_amount = trans_currency.compute(line.transfer_amount,
                                                        company_currency)
                company_fee = trans_currency.compute(line.fee,
                                                     company_currency)
                credit_line_vals = self._prepare_credit_line_vals(
                    company_amount, company_currency)
                dedit_line_vals = self._prepare_dedit_line_vals(
                    company_amount, company_currency)
                credit_line_vals['move_id'] = move.id
                dedit_line_vals['move_id'] = move.id
                credit_line_vals['date'] = line.date_transfer
                dedit_line_vals['date'] = line.date_transfer
                MoveLine.create(credit_line_vals)
                MoveLine.create(dedit_line_vals)
                if company_fee > 0.0:
                    fee_debit_vals = self._prepare_fee_debit_move_lines_vals(
                              company_fee, company_currency)
                    fee_credit_vals = self._prepare_fee_credit_move_lines_vals(
                              company_fee, company_currency)
                    fee_debit_vals['move_id'] = move.id
                    fee_credit_vals['move_id'] = move.id
                    fee_debit_vals['date'] = line.date_transfer
                    fee_credit_vals['date'] = line.date_transfer
                    MoveLine.create(fee_debit_vals)
                    MoveLine.create(fee_credit_vals)
            move.post()
            transfer.write({'state': 'done',
                            'move_id': move.id,
                            'name': move.name,
                            })
        return True

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})


class BankAccountTransferLine(models.Model):
    _name = 'bank.account.transfer.line'

    bank_transfer_id = fields.Many2one(
        'bank.account.transfer',
        string='Bank Account Transfer',
    )
    date_transfer = fields.Date(
        string='Date',
        required=True,
    )
    transfer_amount = fields.Float(
        string='Transfer Amount',
        digits=dp.get_precision('Account'),
        required=True,
    )
    fee = fields.Float(
        string='Fee',
        digits=dp.get_precision('Account'),
        readonly=False,
    )
