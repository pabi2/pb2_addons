# -*- coding: utf-8 -*-
from openerp import models, fields
from .chartfield import MergedChartField


class PurchaseOrderLine(MergedChartField, models.Model):
    _inherit = 'purchase.order.line'
