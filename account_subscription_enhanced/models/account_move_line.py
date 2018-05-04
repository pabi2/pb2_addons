# -*- coding: utf-8 -*-
from openerp import models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def create(self, vals):
        if self._context.get('subline_amount', False):
            if vals.get('debit', False):
                vals['debit'] = self._context.get('subline_amount')
            if vals.get('credit', False):
                vals['credit'] = self._context.get('subline_amount')
        return super(AccountMoveLine, self).create(vals)
