# -*- coding: utf-8 -*-
from openerp import models
from .chartfield import \
    ChartField


class PurchaseRequisitionLine(ChartField, models.Model):
    _inherit = 'purchase.requisition.line'
