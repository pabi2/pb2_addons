# -*- coding: utf-8 -*-

from openerp import models, fields, api


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    cancel_move_id = fields.Many2one(
        'account.move',
        'Cancelled Journal Entry',
        copy=False,
    )
    cancel_reason_txt = fields.Char(
        string="Description",
        readonly=True,
        copy=False,)

    @api.model
    def voucher_move_cancel_hook(self, voucher):
        return

    @api.model
    def write_state_hook(self):
        self.write({
            'state': 'cancel',
        })
        return
