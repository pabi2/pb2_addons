# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    purchase_intransit = fields.Boolean(
        string='Purchase Bank Intransit',
        default=False,
        help="If checked, journal entries of this "
        "journal will show in Bank Payment."
    )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    bank_payment_id = fields.Many2one(
        'account.bank.payment', string='Bank Payment', copy=False)


class AccountMove(models.Model):
    _inherit = 'account.move'

    bank_payment_id = fields.Many2one(
        'account.bank.payment',
        string='Bank Payment',
        compute='_compute_bank_payment',
        store=True,
        readonly=True,
    )

    @api.multi
    @api.depends('line_id.bank_payment_id')
    def _compute_bank_payment(self):
        for move in self:
            if move.bank_payment_id:  # Not yet assigned
                break
            self._cr.execute("""
                select bank_payment_id from account_move_line
                where move_id = %s and bank_payment_id is not null
            """, (move.id, ))
            bank_payment_ids = [i[0] for i in self._cr.fetchall()]
            if bank_payment_ids:
                move.bank_payment_id = bank_payment_ids[0]

    @api.multi
    def create_bank_payment(self, payment_date):
        self._validate_create_bank_payment()
        bank_payment_id = self._create_bank_payment(payment_date)
        return bank_payment_id

    @api.model
    def _prepare_bank_payment(self, move, payment_date):
        res = {'journal_id': move.journal_id.id,
               'payment_date': payment_date,
               'currency_id': (move.journal_id.currency.id or
                               move.journal_id.company_id.currency_id.id),
               }
        return res

    @api.multi
    def _create_bank_payment(self, payment_date):
        first_move = self[0]
        payment_vals = self._prepare_bank_payment(first_move, payment_date)
        domain = [('move_id', 'in', self._ids),  # Find for all selected moves
                  ('reconcile_id', '=', False),
                  ('credit', '>', 0),
                  ('bank_payment_id', '=', False),
                  ('journal_id', '=', first_move.journal_id.id),
                  ('account_id', '=',
                   first_move.journal_id.default_credit_account_id.id)]
        move_line_ids = self.env['account.move.line'].search(domain)._ids
        payment_vals.update({
            'bank_intransit_ids': [(6, 0, list(move_line_ids))]
        })
        bank_payment = self.env['account.bank.payment'].create(payment_vals)
        return bank_payment.id

    @api.multi
    def _validate_create_bank_payment(self):
        # All journal entries must be of same journal_id
        journal_ids = list(set([move.journal_id.id for move in self]))
        if len(journal_ids) > 1:
            raise ValidationError(
                _('Document(s) are not of the same Journal.\n'
                  'Bank Payment creation not allowed'))
        # Check all journal entries must be of Intransit Type
        intransits = [move.journal_id.purchase_intransit for move in self]
        if False in intransits:
            raise ValidationError(
                _('Document(s) not of Journal Type - Intransit.\n'
                  'Bank Payment creation not allowed'))
        # Check Bank Payment not alread created
        payments = [not move.bank_payment_id for move in self]
        if False in payments:
            raise ValidationError(
                _('Document(s) already has Bank Payment.\n'
                  'Bank payment creation not allowed'))
