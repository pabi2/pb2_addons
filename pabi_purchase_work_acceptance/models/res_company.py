# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    delivery_penalty_activity_id = fields.Many2one(
        'account.activity',
        string='Delivery Penalty Activity',
    )
    delivery_penalty_activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Delivery Penalty Activity Group',
    )
