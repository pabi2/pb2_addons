# -*- coding: utf-8 -*-

from openerp import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def _move_reversal(self, reversal_date,
                       reversal_period_id=False, reversal_journal_id=False,
                       move_prefix=False, move_line_prefix=False):
        # Force use prefix for suffix, pass in context
        self = self.with_context(move_prefix=move_prefix)
        reverse_move_id = super(AccountMove, self)._move_reversal(
            reversal_date, reversal_period_id, reversal_journal_id,
            move_prefix, move_line_prefix)
        return reverse_move_id

    @api.model
    def copy(self, default=None):
        move_suffix = self._context.get('move_prefix')
        reversal_ref = ''.join([x for x in [self.ref, move_suffix] if x])
        default.update({'ref': self.ref,
                        'name': reversal_ref})
        return super(AccountMove, self).copy(default)
