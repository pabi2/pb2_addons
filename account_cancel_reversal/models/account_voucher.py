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
        period = self.env['account.period'].find()
        AccountMove = self.env['account.move']
        move_dict = move.copy_data({
            'name': move.name + '_VOID',
            'ref': move.ref,
            'period_id': period.id,
            'date': fields.Date.context_today(self), })[0]
        move_dict = AccountMove._switch_move_dict_dr_cr(move_dict)
        rev_move = AccountMove.create(move_dict)

        voucher.cancel_move_id = rev_move
        # Delete reconcile, and receconcile with reverse entry
        move.line_id.filtered('reconcile_id').reconcile_id.unlink()
        accounts = move.line_id.mapped('account_id')
        for account in accounts:
            AccountMove.\
                _reconcile_voided_entry_by_account([move.id, rev_move.id],
                                                   account.id)

        # self.env['account.move'].\
        #     _reconcile_voided_entry([move.id, rev_move.id])
        return

    @api.model
    def write_state_hook(self):
        self.write({
            'state': 'cancel',
        })
        return

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
