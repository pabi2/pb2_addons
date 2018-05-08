# -*- coding: utf-8 -*-
from openerp import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    activity_rpt_id = fields.Many2one(
        'account.activity',
        string='Activity Rpt',
    )


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    activity_rpt_id = fields.Many2one(
        'account.activity',
        string='Activity Rpt',
        ondelete='restrict',
    )

    @api.model
    def _analytic_dimensions(self):
        dimensions = super(AccountAnalyticAccount, self)._analytic_dimensions()
        dimensions += ['activity_rpt_id']
        return dimensions
