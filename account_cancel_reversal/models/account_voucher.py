# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    cancel_move_id = fields.Many2one(
        'account.move',
        string='Cancel Journal Entry',
        readonly=True,
        index=True,
        ondelete='restrict',
        copy=False,
    )

    @api.model
    def voucher_move_cancel_hook(self, voucher):
        move = voucher.move_id
        rev_move = move.copy({'name': move.name + '_VOID',
                              'ref': move.ref})
        rev_move._switch_dr_cr()
        voucher.cancel_move_id = rev_move
        self.env['account.move'].\
            _reconcile_voided_entry([move.id, rev_move.id])
        return

    @api.model
    def write_state_hook(self):
        self.write({
            'state': 'cancel',
        })
        return

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
