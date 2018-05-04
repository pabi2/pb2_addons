# -*- coding: utf-8 -*-
from openerp import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        if self._context.get('is_clear_prepaid', False):
            # For clear prepayment we don't want to pass invoice number
            self = self.with_context(invoice=False)
        move = super(AccountMove, self).create(vals)
        return move
