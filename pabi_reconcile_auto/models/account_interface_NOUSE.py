# -*- coding: utf-8 -*-
from openerp import models, api


class InterfaceAccountEntry(models.Model):
    _inherit = 'interface.account.entry'

    @api.multi
    def execute(self):
        """ Payment to reconcile invoice is a natural case,
        auto_reconcile_id is not required """
        res = super(InterfaceAccountEntry, self).execute()
        for interface in self:
            ml = interface.mapped('line_ids.reconcile_move_line_ids')
            ml1 = ml.mapped('move_id.line_id')
            if ml1:
                ml2 = interface.move_id.line_id
                mlines = ml1 | ml2
                mlines.reconcile_special_account()
        return res
