# -*- coding: utf-8 -*-
import ast
from openerp import models, api


class AccountMoveReverse(models.TransientModel):
    _inherit = 'account.move.reverse'

    @api.multi
    def action_reverse(self):
        self.ensure_one()
        result = super(AccountMoveReverse, self).action_reverse()
        move_id = self._context.get('active_id')
        move = self.env['account.move'].browse(move_id)
        if move and move.doctype == 'adjustment':
            journal_budget = self.env.ref('pabi_account_move_adjustment.'
                                          'journal_adjust_budget')
            journal_no_budget = self.env.ref('pabi_account_move_adjustment.'
                                             'journal_adjust_no_budget')
            action = False
            if move.journal_id == journal_budget:
                action = self.env.ref('pabi_account_move_adjustment.'
                                      'action_journal_adjust_budget')
            if move.journal_id == journal_no_budget:
                action = self.env.ref('pabi_account_move_adjustment.'
                                      'action_journal_adjust_no_budget')
            if action:
                new_result = action.read()[0]
                domain = ast.literal_eval(new_result['domain']) + \
                    ast.literal_eval(result['domain'])
                new_result['domain'] = domain
                new_result['name'] = result['name']
                new_result['context'] = result['context']
                result = new_result
        return result
