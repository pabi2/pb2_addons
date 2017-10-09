# -*- coding: utf-8 -*-
from datetime import datetime
from openerp import models, fields, api, _


class AccountSubscriptionGenerate(models.TransientModel):
    _inherit = 'account.subscription.generate'

    @api.multi
    def action_generate(self):
        res = super(AccountSubscriptionGenerate, self).action_generate()
        action = self.env.ref('pabi_account_move_adjustment.'
                              'action_journal_adjust_budget')
        result = action.read()[0]
        result.update({'domain': res['domain']})
        return result
