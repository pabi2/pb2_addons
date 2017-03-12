# -*- coding: utf-8 -*-
from openerp import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    rpt_activity_id = fields.Many2one(
        'account.activity',
        string='Rpt Activity',
    )


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    rpt_activity_id = fields.Many2one(
        'account.activity',
        string='Rpt Activity',
        ondelete='restrict',
    )

    @api.model
    def _analytic_dimensions(self):
        dimensions = super(AccountAnalyticAccount, self)._analytic_dimensions()
        dimensions += ['rpt_activity_id']
        return dimensions
