# -*- coding: utf-8 -*-
from openerp import models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def _update_check(self):
        if self._context.get('force_no_update_check', False):
            return True
        return super(AccountMoveLine, self)._update_check()
