# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    ar_late_payment_penalty_activity_id = fields.Many2one(
        'account.activity',
        string='AR Late payment Penalty Activity',
    )
    ar_late_payment_penalty_activity_group_id = fields.Many2one(
        'account.activity.group',
        string='AR Late payment Penalty Activity Group',
    )
