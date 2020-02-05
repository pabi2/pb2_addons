# -*- coding: utf-8 -*-

from openerp import api, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def create(self, vals, **kwargs):
        ctx = self._context.copy()
        ctx.update({'allow_asset': True})
        return super(AccountMoveLine, self).create(vals)
