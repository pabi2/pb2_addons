# -*- coding: utf-8 -*-
from openerp import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def _move_reversal(self, reversal_date,
                       reversal_period_id=False, reversal_journal_id=False,
                       move_prefix=False, move_line_prefix=False):
        reverse_move_id = super(AccountMove, self)._move_reversal(
            reversal_date, reversal_period_id, reversal_journal_id,
            move_prefix, move_line_prefix)
        self.ensure_one()
        reverse_move = self.browse(reverse_move_id)
        if reverse_move.line_id:
            reverse_move.line_id.write(
                {'doc_ref': self.name,
                 'doc_id': '%s,%s' % ('account.move', self.id)})
        return reverse_move_id
