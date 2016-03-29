# -*- coding: utf-8 -*-
from openerp import models
from .chartfield import ChartField


class PurchaseOrderLine(ChartField, models.Model):
    _inherit = 'purchase.order.line'
