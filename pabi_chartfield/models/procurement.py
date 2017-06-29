# -*- coding: utf-8 -*-
from openerp import models, api
from .chartfield import ChartFieldAction


class ProcurementOrder(ChartFieldAction, models.Model):
    _inherit = 'procurement.order'

    @api.model
    def create(self, vals):
        res = super(ProcurementOrder, self).create(vals)
        res.update_related_dimension(vals)
        return res
