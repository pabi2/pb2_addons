# -*- coding: utf-8 -*-
from openerp import models, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def write(self, vals):
        res = super(AccountVoucher, self).write(vals)
        if vals.get('cancel_move_id', False):
            for voucher in self:
                if voucher.doctype_id.reversal_sequence_id:
                    sequence_id = voucher.doctype_id.reversal_sequence_id.id
                    fiscalyear_id = voucher.period_id.fiscalyear_id.id
                    voucher.cancel_move_id.name = self.\
                        with_context(fiscalyear_id=fiscalyear_id).\
                        env['ir.sequence'].next_by_id(sequence_id)
        return res
