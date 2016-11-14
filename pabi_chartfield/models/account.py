# -*- coding: utf-8 -*-
from openerp import models, api
from .chartfield import ChartFieldAction


class AccountModelLine(ChartFieldAction, models.Model):
    _inherit = 'account.model.line'

    @api.model
    def create(self, vals):
        res = super(AccountModelLine, self).create(vals)
        res.update_related_dimension(vals)
        return res
