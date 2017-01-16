# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    title_ids = fields.One2many(
        'pabi.dunning.config.title',
        'config_id',
        string='Prefix Mapping',
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
