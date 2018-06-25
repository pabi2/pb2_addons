# -*- coding: utf-8 -*-
from openerp import fields, models


class InterfaceSystem(models.Model):
    _name = 'interface.system'

    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Char(
        string='Decription',
        required=True,
    )


# class InterfaceAction(models.Model):
#     _name = 'interface.action'
#
#     name = fields.Char(
#         string='Name',
#         required=True,
#     )
#     description = fields.Char(
#         string='Decription',
#         required=True,
#     )
#     journal_id = fields.Many2one(
#         'account.journal',
#         string='Journal',
#     )
