# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountBankReceipt(models.Model):
    _inherit = 'account.bank.receipt'

    cancel_move_id = fields.Many2one(
        'account.move',
        string='Cancel Journal Entry',
        readonly=True,
        index=True,
        ondelete='restrict',
        copy=False,
    )

    @api.model
    def _cancel_move(self):
        for line in self.bank_intransit_ids:
            if line.reconcile_id:
                line.reconcile_id.unlink()
        move = self.move_id
        rev_move = move.copy({'name': move.name + '_VOID',
                              'ref': move.ref})
        rev_move._switch_dr_cr()
        self.cancel_move_id = rev_move
        # As accounto n both DR and CR are balance sheet item, do one by one
        accounts = move.line_id.mapped('account_id')
        print accounts
        for account in accounts:
            self.env['account.move'].\
                _reconcile_voided_entry_by_account([move.id, rev_move.id],
                                                   account.id)
