# -*- coding: utf-8 -*-
from openerp import fields, models


class ResBankBranch(models.Model):
    _name = 'res.bank.branch'
    _description = 'Bank Branch'

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
    bank_id = fields.Many2one(
        'res.bank',
        sring='Bank',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
