# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountType(models.Model):
    _inherit = 'account.account.type'

    for_asset = fields.Boolean(
        string='For Asset Category',
        default=False,
        help="If checked, this account will be selectable in Asset Account."
    )
