# -*- coding: utf-8 -*-
from openerp import models, api


class AccountBankReceipt(models.Model):
    _inherit = 'account.bank.receipt'

    @api.multi
    def write(self, vals):
        res = super(AccountBankReceipt, self).write(vals)
        if vals.get('cancel_move_id', False):
            for receipt in self:
                # get doctype
                refer_type = 'bank_receipt'
                doctype = self.env['res.doctype'].get_doctype(refer_type)
                # --
                if doctype.reversal_sequence_id:
                    sequence_id = doctype.reversal_sequence_id.id
                    fy_id = receipt.cancel_move_id.period_id.fiscalyear_id.id
                    receipt.cancel_move_id.write({
                        'name': self.with_context({'fiscalyear_id': fy_id}).
                        env['ir.sequence'].next_by_id(sequence_id),
                        'cancel_entry': True,
                    })
        return res
