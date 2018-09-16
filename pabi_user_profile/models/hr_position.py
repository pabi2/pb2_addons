# -*- coding: utf-8 -*-
from openerp import fields, models


class HRPosition(models.Model):
    _name = 'hr.position'
    _description = "Master employee's Position"

    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
    )
    code = fields.Char(
        string='Code',
        size=100,
    )
    description = fields.Text(
        string='Description',
        size=1000,
    )
