# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountAssetLocation(models.Model):
    _name = 'account.asset.location'

    name = fields.Char(
        string='Name',
        required=True,
    )
    code = fields.Char(
        string='Code',
        required=False,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
