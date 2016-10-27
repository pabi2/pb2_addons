# -*- coding: utf-8 -*-
from openerp import models, api
from .chartfield import ChartFieldAction


class StockMove(ChartFieldAction, models.Model):
    _inherit = 'stock.move'

    @api.model
    def create(self, vals):
        res = super(StockMove, self).create(vals)
        res.update_related_dimension(vals)
        return res
