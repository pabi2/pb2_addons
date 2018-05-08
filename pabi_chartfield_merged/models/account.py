# -*- coding: utf-8 -*-
from openerp import models
from .chartfield import MergedChartField


class AccountModelLine(MergedChartField, models.Model):
    _inherit = 'account.model.line'
