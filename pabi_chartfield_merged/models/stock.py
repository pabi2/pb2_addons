# -*- coding: utf-8 -*-
from openerp import models
from .chartfield import MergedChartField


class StockMove(MergedChartField, models.Model):
    _inherit = 'stock.move'
