# -*- coding: utf-8 -*-
from openerp import models
from .chartfield import MergedChartField


class PurchaseRequisitionLine(MergedChartField, models.Model):
    _inherit = 'purchase.requisition.line'
