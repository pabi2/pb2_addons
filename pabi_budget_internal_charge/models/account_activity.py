# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountActivity(models.Model):
    _inherit = "account.activity"

    internal_charge = fields.Boolean(
        string='Internal Charge',
        default=False,
        help="For external internal charge, it will refer "
        "to income side internal charge",
    )
    inrev_activity_id = fields.Many2one(
        'account.activity',
        string='Internal Revenue Activity'
    )
