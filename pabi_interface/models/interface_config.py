# -*- coding: utf-8 -*-
from openerp import fields, models


class InterfaceSystem(models.Model):
    _name = 'interface.system'

    name = fields.Char(
        string='Name',
        size=100,
        required=True,
    )
    description = fields.Char(
        string='Decription',
        size=500,
        required=True,
    )
