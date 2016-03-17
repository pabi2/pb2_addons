# -*- coding: utf-8 -*-

from openerp import models, api, _
from openerp.exceptions import except_orm


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def action_cancel_hook(self, moves=False):
        self.write({'state': 'cancel', 'move_id': False})
        if moves:
            # second, invalidate the move(s)
            moves.button_cancel()
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            moves.unlink()
        return

    @api.multi
    def action_cancel(self):
        moves = self.env['account.move']
        for inv in self:
            if inv.move_id:
                moves += inv.move_id
            if inv.payment_ids:
                for move_line in inv.payment_ids:
                    if move_line.reconcile_partial_id.line_partial_ids:
                        raise except_orm(_('Error!'),
                                         _('You cannot cancel an invoice\
                                         which is partially paid. You need\
                                         to unreconcile related payment \
                                         entries first.'))

        # First, set the invoices as cancelled and detach the move ids
        self.action_cancel_hook(moves)  # hook
        self._log_event(-1.0, 'Cancel Invoice')
        return True
