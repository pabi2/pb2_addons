# -*- coding: utf-8 -*-

from openerp import models
from .chartfield import ChartField


class PurchaseRequestLineMakePurchaseRequisitionItem(ChartField,
                                                     models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition.item"
