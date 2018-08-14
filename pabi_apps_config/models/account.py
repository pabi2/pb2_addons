# -*- coding: utf-8 -*-
from openerp import models, api


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # Do not show view account
        args = args or []
        if not self._context.get('show_account_view', False):
            args += [('type', '!=', 'view')]
        return super(AccountAccount, self).name_search(name=name, args=args,
                                                       operator=operator,
                                                       limit=limit)
