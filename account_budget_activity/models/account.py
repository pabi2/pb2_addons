# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountFiscalyear(models.Model):
    _inherit = 'account.fiscalyear'

    budgeting_level = fields.Selection(
        [('activity_group_id', 'Activity Group'),
         ('activity_id', 'Activity'), ],
        string='Budgeting Level',
        required=True,
        default='activity_group_id',
    )
