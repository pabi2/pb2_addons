# -*- coding: utf-8 -*-
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):
        result = super(AccountInvoice, self).action_move_create()
        for invoice in self:
            if invoice.move_id:
                invoice.move_id.line_id.write({'doc_ref': invoice.number})
        return result
