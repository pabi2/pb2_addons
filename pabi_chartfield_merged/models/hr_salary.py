# -*- coding: utf-8 -*-
from openerp import models, fields
from .chartfield import MergedChartField


class HRSalaryLine(MergedChartField, models.Model):
    _inherit = 'hr.salary.line'

    chartfield_id = fields.Many2one(
        domain=[],
    )
