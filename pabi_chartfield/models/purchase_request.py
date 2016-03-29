# -*- coding: utf-8 -*-
from openerp import models
from .chartfield import ChartField


class PurchaseRequestLine(ChartField, models.Model):
    _inherit = 'purchase.request.line'
