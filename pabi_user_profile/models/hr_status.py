# -*- coding: utf-8 -*-
from openerp import fields, models


class HRStatus(models.Model):
    _name = 'hr.status'
    _description = "Master employee's status"

    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
        size=100,
    )
    code = fields.Char(
        string='Code',
        size=100,
    )
    control_active = fields.Boolean(
        string='Control Active',
        default=True,
    )
