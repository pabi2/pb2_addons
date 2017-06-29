# -*- coding: utf-8 -*-
from openerp import fields, models


class PABIDunningConfig(models.TransientModel):
    _name = 'pabi.dunning.config'
    _inherit = 'res.config.settings'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )
    title_ids = fields.One2many(
        'pabi.dunning.config.title',
        string='Prefix Mapping',
        related='company_id.title_ids',
    )
    # Subject
    letter1_subject = fields.Char(
        string='Letter 1 Subject',
        related='company_id.letter1_subject',
        translate=True,
    )
    letter2_subject = fields.Char(
        string='Letter 2 Subject',
        related='company_id.letter2_subject',
        translate=True,
    )
    letter3_subject = fields.Char(
        string='Letter 3 Subject',
        related='company_id.letter3_subject',
        translate=True,
    )
    # Letter 1
    letter1_header = fields.Text(
        string='Letter 1 Header',
        related='company_id.letter1_header',
        translate=True,
    )
    letter1_footer = fields.Text(
        string='Letter 1 Footer',
        related='company_id.letter1_footer',
        translate=True,
    )
    letter1_signature = fields.Text(
        string='Letter 1 Signature',
        related='company_id.letter1_signature',
        translate=True,
    )
    # Letter 2
    letter2_header = fields.Text(
        string='Letter 2 Header',
        related='company_id.letter2_header',
        translate=True,
    )
    letter2_footer = fields.Text(
        string='Letter 2 Footer',
        related='company_id.letter2_footer',
        translate=True,
    )
    letter2_signature = fields.Text(
        string='Letter 2 Signature',
        related='company_id.letter2_signature',
        translate=True,
    )
    # Letter 3
    letter3_header = fields.Text(
        string='Letter 3 Header',
        related='company_id.letter3_header',
        translate=True,
    )
    letter3_footer = fields.Text(
        string='Letter 3 Footer',
        related='company_id.letter3_footer',
        translate=True,
    )
    letter3_signature = fields.Text(
        string='Letter 3 Signature',
        related='company_id.letter3_signature',
        translate=True,
    )


class PABIDunningConfigTitle(models.Model):
    _name = 'pabi.dunning.config.title'

    config_id = fields.Many2one(
        'res.company',
        string='Dunning Config',
        index=True,
        readonly=True,
    )
    title_id = fields.Many2one(
        'res.partner.title',
        string='Title',
        required=True,
    )
    new_title = fields.Char(
        string='New Title',
        required=True,
    )
