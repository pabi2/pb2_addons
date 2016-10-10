# -*- coding: utf-8 -*-
from openerp import models, fields


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    # Special Field, to be used as extension point for other th modules
    special_type = fields.Selection(
        [],
        string='Special Type',
    )
