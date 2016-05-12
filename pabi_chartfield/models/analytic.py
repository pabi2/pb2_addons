# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import api, models
from .chartfield import CHART_FIELDS, ChartFieldAction


class AccountAnalyticLine(ChartFieldAction, models.Model):
    _inherit = 'account.analytic.line'


class AccountAnalyticAccount(ChartFieldAction, models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _analytic_dimensions(self):
        dimensions = super(AccountAnalyticAccount, self)._analytic_dimensions()
        dimensions += dict(CHART_FIELDS).keys()
        return dimensions
