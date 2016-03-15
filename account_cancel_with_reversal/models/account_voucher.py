# -*- coding: utf-8 -*-

from openerp import models, fields,  api, _


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    cancel_move_id = fields.Many2one('account.move', 'Cancelled Journal Entry')

    @api.multi
    def cancel_voucher(self):
        """ Overwrite """
        if self.env.context is None:
            self.env.context = {}
        reconcile_pool = self.env['account.move.reconcile']
        move_pool = self.env['account.move']
        move_line_pool = self.env['account.move.line']
        for voucher in self:
            # refresh to make sure you don't unlink an already removed move
            voucher.refresh()
            for line in voucher.move_ids:
                # refresh to make sure you don't
                # unreconcile an already unreconciled entry
                line.refresh()
                if line.reconcile_id:
                    move_lines = [move_line.id for move_line in
                                  line.reconcile_id.line_id]
                    move_lines.remove(line.id)
                    line.reconcile_id.unlink()
                    if len(move_lines) >= 2:
                        move_line_pool.reconcile_partial(move_lines, 'auto')
        return self.write({'state': 'cancel'})
