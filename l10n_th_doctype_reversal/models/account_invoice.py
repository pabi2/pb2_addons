# -*- coding: utf-8 -*-
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        if vals.get('cancel_move_id', False):
            for invoice in self:
                if invoice.doctype_id.reversal_sequence_id:
                    sequence_id = invoice.doctype_id.reversal_sequence_id.id
                    fy_id = invoice.period_id.fiscalyear_id.id
                    invoice.cancel_move_id.write({
                        'name': self.with_context(fiscalyear_id=fy_id).
                        env['ir.sequence'].next_by_id(sequence_id),
                        'cancel_entry': True,
                    })
        return res
