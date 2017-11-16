# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import api, models, fields
from .chartfield import CHART_FIELDS, ChartFieldAction


class AccountAnalyticLine(ChartFieldAction, models.Model):
    _inherit = 'account.analytic.line'

    # ChartfieldAction changed account_id = account.account, must change back
    account_id = fields.Many2one('account.analytic.account')


class AccountAnalyticAccount(ChartFieldAction, models.Model):
    _inherit = 'account.analytic.account'

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        required=True,  # Some error on adjust asset -> expense, temp remove
    )

    @api.model
    def _analytic_dimensions(self):
        dimensions = super(AccountAnalyticAccount, self)._analytic_dimensions()
        dimensions += dict(CHART_FIELDS).keys()
        return dimensions
