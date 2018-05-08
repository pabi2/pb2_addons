# -*- coding: utf-8 -*-
from openerp import models, api
from .chartfield import ChartFieldAction


class PurchaseRequestLine(ChartFieldAction, models.Model):
    _inherit = 'purchase.request.line'

    @api.model
    def create(self, vals):
        res = super(PurchaseRequestLine, self).create(vals)
        res.update_related_dimension(vals)
        return res
