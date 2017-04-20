# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    ar_late_payment_penalty_activity_id = fields.Many2one(
        'account.activity',
        string='AR Late payment Penalty Activity',
        related="company_id.ar_late_payment_penalty_activity_id",
        domain="[('activity_group_ids', 'in',"
               "[ar_late_payment_penalty_activity_group_id or -1])]",
    )
    ar_late_payment_penalty_activity_group_id = fields.Many2one(
        'account.activity.group',
        string='AR Late payment Penalty Activity Group',
        related="company_id.ar_late_payment_penalty_activity_group_id",
    )
