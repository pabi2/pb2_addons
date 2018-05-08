# -*- coding: utf-8 -*-
from openerp import models
from .chartfield import MergedChartField


class PurchaseRequestLine(MergedChartField, models.Model):
    _inherit = 'purchase.request.line'
