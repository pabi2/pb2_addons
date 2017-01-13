# -*- coding: utf-8 -*-
from openerp import fields, models, api


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
    signature_dunning = fields.Text(
        string='Signature for Dunning',
        related='company_id.signature_dunning',
    )
    signature_litigation = fields.Text(
        string='Signature for Litigation',
        related='company_id.signature_litigation',
    )
    account_dept_contact = fields.Text(
        string='Account Dept. Contact',
        related='company_id.account_dept_contact',
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
