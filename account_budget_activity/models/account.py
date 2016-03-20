# -*- coding: utf-8 -*-
from openerp import fields, models

BUDGETING_LEVEL = {
    'activity_group_id': 'Activity Group',
    'activity_id': 'Activity'
}


class AccountFiscalyear(models.Model):
    _inherit = 'account.fiscalyear'

    budget_control = fields.Boolean(
        string='Budget Control',
        default=False,
    )
    budgeting_level = fields.Selection(
        BUDGETING_LEVEL.items(),
        string='Budgeting Level',
        required=True,
        default='activity_group_id',
    )
