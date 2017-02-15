# -*- coding: utf-8 -*-
from openerp import models, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def write(self, vals):
        res = super(AccountVoucher, self).write(vals)
        if vals.get('cancel_move_id', False):
            for voucher in self:
                # get doctype
                refer_type = voucher.type
                doctype = self.env['res.doctype'].get_doctype(refer_type)
                # --
                if doctype.reversal_sequence_id:
                    sequence_id = doctype.reversal_sequence_id.id
                    fy_id = voucher.cancel_move_id.period_id.fiscalyear_id.id
                    voucher.cancel_move_id.write({
                        'name': self.with_context({'fiscalyear_id': fy_id}).
                        env['ir.sequence'].next_by_id(sequence_id),
                        'cancel_entry': True,
                    })
        return res
