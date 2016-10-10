# -*- coding: utf-8 -*-
from openerp import models, fields


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    is_asset_number = fields.Boolean(
        string='Asset Number',
        default=False,
    )
