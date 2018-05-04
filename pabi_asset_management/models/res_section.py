# -*- coding: utf-8 -*-
from openerp import models, fields


class ResSection(models.Model):
    _inherit = 'res.section'

    asset_ids = fields.One2many(
        'account.asset',
        'owner_section_id',
        string='Assets',
    )
