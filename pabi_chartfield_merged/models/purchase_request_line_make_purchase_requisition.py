# -*- coding: utf-8 -*-
from openerp import models
from .chartfield import MergedChartField


class PurchaseRequestLineMakePurchaseRequisitionItem(MergedChartField,
                                                     models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition.item"
