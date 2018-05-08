# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=False,
    )
