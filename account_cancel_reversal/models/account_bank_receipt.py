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
        period = self.env['account.period'].find()
        AccountMove = self.env['account.move']
        move_dict = move.copy_data({
            'name': move.name + '_VOID',
            'ref': move.ref,
            'period_id': period.id,
            'date': fields.Date.context_today(self), })[0]
        move_dict = AccountMove._switch_move_dict_dr_cr(move_dict)
        rev_move = AccountMove.create(move_dict)
        self.cancel_move_id = rev_move
        # As account both DR and CR are balance sheet item, do one by one
        accounts = move.line_id.mapped('account_id')
        for account in accounts:
            AccountMove.\
                _reconcile_voided_entry_by_account([move.id, rev_move.id],
                                                   account.id)
