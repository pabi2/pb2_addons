# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    title_ids = fields.One2many(
        'pabi.dunning.config.title',
        'config_id',
        string='Prefix Mapping',
    )
    litigation_contact = fields.Char(
        string='Legal Dept. Contact',
    )
    signature_dunning = fields.Text(
        string='Signature for Dunning',
    )
    signature_litigation = fields.Text(
        string='Signature for Litigation',
    )
    account_dept_contact = fields.Text(
        string='Account Dept. Contact',
    )
    # EN
    litigation_contact_en = fields.Char(
        string='Legal Dept. Contact (EN)',
    )
    signature_dunning_en = fields.Text(
        string='Signature for Dunning (EN)',
    )
    signature_litigation_en = fields.Text(
        string='Signature for Litigation (EN)',
    )
    account_dept_contact_en = fields.Text(
        string='Account Dept. Contact (EN)',
    )
