# -*- coding: utf-8 -*-

from openerp import models, api
from .chartfield import ChartFieldAction


class PurchaseRequestLineMakePurchaseRequisitionItem(ChartFieldAction,
                                                     models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition.item"

    @api.model
    def create(self, vals):
        res = super(PurchaseRequestLineMakePurchaseRequisitionItem,
                    self).create(vals)
        res.update_related_dimension(vals)
        return res
