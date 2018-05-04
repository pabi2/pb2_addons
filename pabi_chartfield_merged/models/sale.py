# -*- coding: utf-8 -*-
from openerp import models
from .chartfield import MergedChartField


class SaleOrderLine(MergedChartField, models.Model):
    _inherit = 'sale.order.line'
