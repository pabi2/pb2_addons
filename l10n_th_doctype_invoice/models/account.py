# -*- coding: utf-8 -*-
from openerp import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self):
        if not self._context.get('doctype_id', False):
            return super(AccountMove, self).post()
        # Because the post method do not pass all context, we need to fake it
        invoice = self._context.get('invoice', False)
        if invoice:
            for move in self:
                if invoice.internal_number:
                    move.name = invoice.internal_number
                    invoice.number = invoice.internal_number
                else:
                    self = self.with_context(
                        fiscalyear_id=move.period_id.fiscalyear_id.id)
                    # Because we have doctype_id, so we can pass False
                    name = self.env['ir.sequence'].next_by_id(False)
                    move.name = name
                    invoice.write({'number': name, 'internal_number': name})
        return super(AccountMove, self).post()
