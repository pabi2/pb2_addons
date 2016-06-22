# -*- coding: utf-8 -*-
from openerp import fields, models


# Personnel
class ResPersonnelCostcenter(models.Model):
    _name = 'res.personnel.costcenter'
    _description = 'Personnel Budget'

    name = fields.Char(
        string='Name',
        required=True,
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        required=False,
    )
