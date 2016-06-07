# -*- coding: utf-8 -*-
from openerp import fields, models


# Personnel
class ResPersonnelCostcenter(models.Model):
    _name = 'res.personnel.costcenter'
    _description = 'Personnel Costcenter'

    name = fields.Char(
        string='Name',
        required=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=False,
    )
