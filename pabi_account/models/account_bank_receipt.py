# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountBankReceipt(models.Model):
    _inherit = "account.bank.receipt"

    partner_bank_id = fields.Many2one(
        'res.partner.bank',
        domain="[('partner_id', '=', company_partner_id)]",
        required=False,
    )
    bank_account_id = fields.Many2one(
        'account.account',
        related=False,
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    receipt_date = fields.Date(
        string='Posting Date',  # Change label
    )
    date_document = fields.Date(
        string='Document Date',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
        default=lambda self: fields.Date.context_today(self),
    )
    date_accept = fields.Date(
        string='Accepted Date',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    # For cancel invoice case
    cancel_date_document = fields.Date(
        string='Cancel Document Date',
    )
    cancel_date = fields.Date(
        string='Cancel Posting Date',
    )

    @api.multi
    def write(self, vals):
        # Set date
        if vals.get('receipt_date') and not vals.get('date_document'):
            for rec in self:
                if not rec.date_document:
                    vals['date_document'] = vals['receipt_date']
                    break
        return super(AccountBankReceipt, self).write(vals)

    @api.onchange('bank_account_id')
    def onchange_bank_account_id(self):
        self.partner_bank_id = False
        if self.bank_account_id:
            Journal = self.env['account.journal']
            BankAcct = self.env['res.partner.bank']
            journals = Journal.search([('default_debit_account_id', '=',
                                        self.bank_account_id.id)])
            banks = BankAcct.search([('journal_id', 'in', journals.ids),
                                     ('state', '=', 'SA')])
            self.partner_bank_id = banks and banks[0] or False

    @api.multi
    def _prepare_analytic_line_vals(self, line):
        self.ensure_one()
        vals = {
            'account_id': line.analytic_account_id.id,
            'general_account_id': line.account_id.id,
            'date': self.date_document,
            'move_id': line.id,
            'name': line.name,
            'user_id': 1,
            'journal_id': self.move_id.journal_id.analytic_journal_id.id,
            'amount': line.debit and -line.debit or line.credit,
            'ref': self.name
        }
        return vals

    @api.multi
    def action_recompute_budget(self):
        AnalyticLine = self.env['account.analytic.line'].sudo()
        for rec in self:
            # skip if not payment diff or check budget already
            payment_diff = rec.multiple_reconcile_ids
            analytic_line = rec.move_id.budget_commit_ids
            if not payment_diff or (payment_diff and analytic_line):
                continue
            if not rec.move_id.journal_id.analytic_journal_id:
                raise ValidationError(_(
                    'Journal %s is not set check budget'
                    % rec.move_id.journal_id.name))
            # Find analytic_account from account.move.line
            move_line = rec.move_id.line_id.filtered(
                lambda l: l.analytic_account_id)
            for line in move_line:
                vals = rec._prepare_analytic_line_vals(line)
                AnalyticLine.create(vals)

    @api.multi
    def _prepare_reverse_move_data(self):
        self.ensure_one()
        res = super(AccountBankReceipt, self)._prepare_reverse_move_data()
        # If cancel data available, use it.
        if self.cancel_date_document:
            res.update({'date_document': self.cancel_date_document})
        if self.cancel_date:
            periods = self.env['account.period'].find(self.cancel_date)
            period = periods and periods[0] or False
            res.update({'date': self.cancel_date,
                        'period_id': period.id})
        return res
