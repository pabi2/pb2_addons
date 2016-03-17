# -*- coding: utf-8 -*-

from openerp import models, api


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    @api.model
    def voucher_move_cancel_hook(self, voucher):
        voucher.move_id.button_cancel()
        voucher.move_id.unlink()
        return

    @api.model
    def write_state_hook(self):
        self.write({
            'state': 'cancel',
            'move_id': False,
        })
        return

    @api.multi
    def cancel_voucher(self):
        for voucher in self:
            # refresh to make sure you don't unlink an already removed move
            voucher.refresh()
            for line in voucher.move_ids:
                # refresh to make sure you don't unreconcile
                # an already unreconciled entry
                line.refresh()
                if line.reconcile_id:
                    move_lines = [move_line.id
                                  for move_line in line.reconcile_id.line_id]
                    move_lines.remove(line.id)
                    line.reconcile_id.unlink()
                    if len(move_lines) >= 2:
                        move_lines.reconcile_partial('auto')
            if voucher.move_id:
                self.voucher_move_cancel_hook(voucher)  # HOOK
        self.write_state_hook()
        return True
