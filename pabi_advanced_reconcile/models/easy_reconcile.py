# -*- coding: utf-8 -*-
from openerp import models, api


class AccountEasyReconcileMethod(models.Model):
    _inherit = 'account.easy.reconcile.method'

    @api.multi
    def _get_all_rec_method(self):
        methods = super(AccountEasyReconcileMethod, self
                        )._get_all_rec_method()
        methods += [
            ('easy.reconcile.advanced.account',
             'Advanced. Account.'),
        ]
        return methods
