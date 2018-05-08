# -*- coding: utf-8 -*-
from openerp import models, api


class AccountUseModel(models.TransientModel):
    _inherit = 'account.use.model'

    @api.multi
    def create_entries(self):
        res = super(AccountUseModel, self).create_entries()
        res.pop('views')
        return res
