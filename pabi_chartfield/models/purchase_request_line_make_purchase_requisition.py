# -*- coding: utf-8 -*-

from openerp import models
from .chartfield import ChartFieldAction


class PurchaseRequestLineMakePurchaseRequisitionItem(ChartFieldAction,
                                                     models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition.item"
