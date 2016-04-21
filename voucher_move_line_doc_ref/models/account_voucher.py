# -*- coding: utf-8 -*-
from openerp import models, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.v7
    def action_move_line_create(self, cr, uid, ids, context=None):
        result = super(AccountVoucher, self).\
            action_move_line_create(cr, uid, ids, context=context)
        for voucher in self.browse(cr, uid, ids, context):
            if voucher.move_id:
                voucher.move_id.line_id.write({'doc_ref': voucher.number})
                self.pool.get('account.move.line').write(
                    cr, uid,
                    voucher.move_id.line_id.ids,
                    {'doc_ref': voucher.number}
                )
        return result
