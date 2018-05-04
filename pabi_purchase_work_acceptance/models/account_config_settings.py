# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    delivery_penalty_activity_id = fields.Many2one(
        'account.activity',
        string='Delivery Penalty Activity',
        related="company_id.delivery_penalty_activity_id",
        domain="[('activity_group_ids', 'in',"
               "[delivery_penalty_activity_group_id or -1])]",
    )
    delivery_penalty_activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Delivery Penalty Activity Group',
        related="company_id.delivery_penalty_activity_group_id",
    )
