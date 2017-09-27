# -*- coding: utf-8 -*-
from openerp import models, api


class AccountUseModel(models.TransientModel):
    _inherit = 'account.use.model'

    @api.multi
    def create_entries(self):
        end_period_date = self.env['account.period'].find().date_stop
        self = self.with_context(end_period_date=end_period_date)
        res = super(AccountUseModel, self).create_entries()
        return res
