# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    intransit = fields.Boolean(
        string='Bank Intransit',
        default=False,
        help="If checked, journal entries of this "
        "journal will show in Bank Receipt."
    )


class AccountMove(models.Model):
    _inherit = 'account.move'

    bank_receipt_id = fields.Many2one(
        'account.bank.receipt',
        string='Bank Receipt',
        compute='_compute_bank_receipt',
        store=True,
        readonly=True,
    )

    @api.multi
    @api.depends('line_id.bank_receipt_id')
    def _compute_bank_receipt(self):
        for move in self:
            bank_receipt_line = move.line_id.filtered('bank_receipt_id')
            move.bank_receipt_id = bank_receipt_line.bank_receipt_id
            if move.bank_receipt_id:
                break

    @api.multi
    def create_bank_receipt(self, receipt_date):
        self._validate_create_bank_receipt()
        bank_receipt_id = self._create_bank_receipt(receipt_date)
        return bank_receipt_id

    @api.model
    def _prepare_bank_receipt(self, move, receipt_date):
        res = {'journal_id': move.journal_id.id,
               'receipt_date': receipt_date,
               'currency_id': (move.journal_id.currency.id or
                               move.journal_id.company_id.currency_id.id),
               }
        return res

    @api.multi
    def _create_bank_receipt(self, receipt_date):
        first_move = self[0]
        receipt_vals = self._prepare_bank_receipt(first_move, receipt_date)
        domain = [('move_id', 'in', self._ids),  # Find for all selected moves
                  ('reconcile_id', '=', False),
                  ('debit', '>', 0),
                  ('bank_receipt_id', '=', False),
                  ('journal_id', '=', first_move.journal_id.id),
                  ('account_id', '=',
                   first_move.journal_id.default_debit_account_id.id)]
        move_line_ids = self.env['account.move.line'].search(domain)._ids
        receipt_vals.update({
            'bank_intransit_ids': [(6, 0, list(move_line_ids))]
        })
        bank_receipt = self.env['account.bank.receipt'].create(receipt_vals)
        return bank_receipt.id

    @api.multi
    def _validate_create_bank_receipt(self):
        # All journal entries must be of same journal_id
        journal_ids = list(set([move.journal_id.id for move in self]))
        if len(journal_ids) > 1:
            raise ValidationError(
                _('Document(s) are not of the same Journal.\n'
                  'Bank Receipt creation not allowed'))
        # Check all journal entries must be of Intransit Type
        intransits = [move.journal_id.intransit for move in self]
        if False in intransits:
            raise ValidationError(
                _('Document(s) not of Journal Type - Intransit.\n'
                  'Bank Receipt creation not allowed'))
        # Check Bank Receipt not alread created
        receipts = [not move.bank_receipt_id for move in self]
        if False in receipts:
            raise ValidationError(
                _('Document(s) already has Bank Receipt.\n'
                  'Bank Receipt creation not allowed'))
