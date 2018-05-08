# -*- coding: utf-8 -*-
from openerp import api, models
from .chartfield import ChartFieldAction


class HRSalaryLine(ChartFieldAction, models.Model):
    _inherit = 'hr.salary.line'

    @api.model
    def create(self, vals):
        res = super(HRSalaryLine, self).create(vals)
        res.update_related_dimension(vals)
        return res
