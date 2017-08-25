# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _


class AccountUseModel(models.TransientModel):
    _inherit = 'account.use.model'

    @api.multi
    def create_entries(self):
        end_period_date = self.env['account.period'].find().date_stop
        self = self.with_context(end_period_date=end_period_date)
        return super(AccountUseModel, self).create_entries()
