# -*- coding: utf-8 -*-
from openerp import fields, models


class SystemOrigin(models.Model):
    _name = 'system.origin'

    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Char(
        string='Decription',
        required=True,
    )
