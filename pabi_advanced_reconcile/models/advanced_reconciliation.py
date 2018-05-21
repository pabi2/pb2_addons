# -*- coding: utf-8 -*-
from openerp import models, api


class EasyReconcileAdvancedAccount(models.TransientModel):
    _name = 'easy.reconcile.advanced.account'
    _inherit = 'easy.reconcile.advanced'

    @api.multi
    def _skip_line(self, move_line):
        return not move_line.get('account_id')

    @api.multi
    def _matchers(self, move_line):
        return (('account_id', move_line['account_id']), )

    @api.multi
    def _opposite_matchers(self, move_line):
        yield ('account_id', move_line['account_id'])
