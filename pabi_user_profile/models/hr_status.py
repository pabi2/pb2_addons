# -*- coding: utf-8 -*-
from openerp import fields, models


class HRStatus(models.Model):
    _name = 'hr.status'
    _description = "Master employee's status"

    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
    )
    code = fields.Char(
        string='Code',
    )
    control_active = fields.Boolean(
        string='Control Active',
        default=True,
    )
