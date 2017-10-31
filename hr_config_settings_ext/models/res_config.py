# -*- coding: utf-8 -*-
from openerp import models, fields


class HRConfigSettings(models.TransientModel):
    _inherit = 'hr.config.settings'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )
