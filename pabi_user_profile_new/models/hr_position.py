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
    )
    description = fields.Text(
        string='Description',
    )
