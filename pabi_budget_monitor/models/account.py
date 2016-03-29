# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountFiscalyear(models.Model):
    _inherit = 'account.fiscalyear'

    # Overwrite budgeting_level
    budgeting_level = fields.Selection(
        lambda self: self.env['account.budget'].BUDGETING_LEVEL.items(),
        string='Project Based - Budgeting Level',
        required=True,
        default='program_id',
    )
    budgeting_level_unit = fields.Selection(
        lambda self: self.env['account.budget'].BUDGETING_LEVEL_UNIT.items(),
        string='Unit Based - Budgeting Level',
        required=True,
        default='activity_group_id',
    )
