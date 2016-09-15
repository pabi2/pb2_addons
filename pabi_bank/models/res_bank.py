# -*- coding: utf-8 -*-
from openerp import fields, models


class ResBankMaster(models.Model):
    _name = 'res.bank.master'
    _description = 'Bank Master Data'

    name = fields.Char(
        string='Name',
        translate=True,
        required=True,
    )
    code = fields.Char(
        string='Code',
        required=True,
    )
    abbrev = fields.Char(
        string='Abbreviation',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
