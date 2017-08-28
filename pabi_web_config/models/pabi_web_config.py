# -*- coding: utf-8 -*-
from openerp import fields, models


class PABIWebConfigSettings(models.TransientModel):
    _name = 'pabi.web.config.settings'
    _inherit = 'res.config.settings'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )
    pabiweb_active = fields.Boolean(
        string="Open Connection to PABI Web.",
        related='company_id.pabiweb_active',
    )
    pabiweb_hr_url = fields.Char(
        string='PABI Web URL for HR Salary',
        related='company_id.pabiweb_hr_url',
    )
    pabiweb_exp_url = fields.Char(
        string='PABI Web URL for Expense',
        related='company_id.pabiweb_exp_url',
    )
    pabiweb_pcm_url = fields.Char(
        string='PABI Web URL for Procurement',
        related='company_id.pabiweb_pcm_url',
    )
    pabiweb_file_prefix = fields.Char(
        string='PABI Web URL for attachment prefix',
        related='company_id.pabiweb_file_prefix',
    )
