# -*- coding: utf-8 -*-
from openerp import models
from .chartfield import ChartFieldAction


class PurchaseRequestLine(ChartFieldAction, models.Model):
    _inherit = 'purchase.request.line'
