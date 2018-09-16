# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    title_ids = fields.One2many(
        'pabi.dunning.config.title',
        'config_id',
        string='Prefix Mapping',
    )
    letter1_subject = fields.Char(
        string='Letter 1 Subject',
        translate=True,
        size=500,
    )
    letter2_subject = fields.Char(
        string='Letter 2 Subject',
        translate=True,
        size=500,
    )
    letter3_subject = fields.Char(
        string='Letter 3 Subject',
        translate=True,
    )
    letter1_header = fields.Text(
        string='Letter 1 Header',
        translate=True,
        size=500,
    )
    letter1_footer = fields.Text(
        string='Letter 1 Footer',
        translate=True,
        size=1000,
    )
    letter1_signature = fields.Text(
        string='Letter 1 Signature',
        translate=True,
        size=1000,
    )
    letter2_header = fields.Text(
        string='Letter 2 Header',
        translate=True,
        size=1000,
    )
    letter2_footer = fields.Text(
        string='Letter 2 Footer',
        translate=True,
        size=1000,
    )
    letter2_signature = fields.Text(
        string='Letter 2 Signature',
        translate=True,
        size=1000,
    )
    letter3_header = fields.Text(
        string='Letter 3 Header',
        translate=True,
        size=1000,
    )
    letter3_footer = fields.Text(
        string='Letter 3 Footer',
        translate=True,
        size=1000,
    )
    letter3_signature = fields.Text(
        string='Letter 3 Signature',
        translate=True,
        size=1000,
    )
