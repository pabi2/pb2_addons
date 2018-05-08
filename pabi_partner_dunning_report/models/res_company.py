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
    )
    letter2_subject = fields.Char(
        string='Letter 2 Subject',
        translate=True,
    )
    letter3_subject = fields.Char(
        string='Letter 3 Subject',
        translate=True,
    )
    letter1_header = fields.Text(
        string='Letter 1 Header',
        translate=True,
    )
    letter1_footer = fields.Text(
        string='Letter 1 Footer',
        translate=True,
    )
    letter1_signature = fields.Text(
        string='Letter 1 Signature',
        translate=True,
    )
    letter2_header = fields.Text(
        string='Letter 2 Header',
        translate=True,
    )
    letter2_footer = fields.Text(
        string='Letter 2 Footer',
        translate=True,
    )
    letter2_signature = fields.Text(
        string='Letter 2 Signature',
        translate=True,
    )
    letter3_header = fields.Text(
        string='Letter 3 Header',
        translate=True,
    )
    letter3_footer = fields.Text(
        string='Letter 3 Footer',
        translate=True,
    )
    letter3_signature = fields.Text(
        string='Letter 3 Signature',
        translate=True,
    )
