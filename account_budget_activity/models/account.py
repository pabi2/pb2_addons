# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountFiscalyear(models.Model):
    _inherit = 'account.fiscalyear'

    budget_control = fields.Boolean(
        string='Budget Control',
        default=False,
    )
    budgeting_level = fields.Selection(
        lambda self: self.env['account.budget'].BUDGETING_LEVEL.items(),
        string='Budgeting Level',
        required=True,
        default='activity_group_id',
    )
