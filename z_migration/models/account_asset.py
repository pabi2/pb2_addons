# -*- coding: utf-8 -*-
from openerp import models, api


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    @api.multi
    def mork_compute_depreciation_board(self):
        self.compute_depreciation_board()
        return True

    @api.multi
    def mork_validate(self):
        self.validate()
        return True
