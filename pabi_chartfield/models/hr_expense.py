# -*- coding: utf-8 -*-
from openerp import models
from .chartfield import ChartField


class HRExpenseLine(ChartField, models.Model):
    _inherit = 'hr.expense.line'
