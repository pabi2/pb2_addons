# -*- coding: utf-8 -*-
from openerp import models
from .chartfield import MergedChartField


class HRExpenseLine(MergedChartField, models.Model):
    _inherit = 'hr.expense.line'
