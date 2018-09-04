# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountAssetLine(models.Model):
    _inherit = 'account.asset.line'

    line_days = fields.Integer(
        string='Days',
        readonly=False,
    )
