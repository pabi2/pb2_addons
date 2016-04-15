# -*- coding: utf-8 -*-
from openerp import models, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def action_move_line_create(self):
        result = super(AccountVoucher, self).action_move_line_create()
        for voucher in self:
            if voucher.move_id:
                voucher.move_id.line_id.write({'doc_ref': voucher.number})
        return result
