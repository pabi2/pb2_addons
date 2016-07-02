# -*- coding: utf-8 -*-
from openerp import fields, models
from openerp.addons.pabi_base.models.res_common import ResCommon


# Personnel
class ResPersonnelCostcenter(ResCommon, models.Model):
    _name = 'res.personnel.costcenter'
    _description = 'Personnel Budget'

    section_id = fields.Many2one(
        'res.section',
        string='Section',
        required=False,
    )
