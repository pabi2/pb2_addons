# -*- coding: utf-8 -*-
from openerp import fields, models


class AccessGroup(models.Model):
    _name = "access.access"

    name = fields.Char(string="Meta Group")
    groups_id = fields.Many2many('res.groups',
                                 'group_access',
                                 'id', 'group_id',
                                 string='Groups')
