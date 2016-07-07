# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import models, api
from .chartfield import ChartField


class AccountMoveLine(ChartField, models.Model):
    _inherit = 'account.move.line'

    @api.model
    def create(self, vals):
        res = super(AccountMoveLine, self).create(vals)
        res.update_related_dimension(vals)
        return res
