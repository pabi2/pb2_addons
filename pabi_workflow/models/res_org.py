# -*- coding: utf-8 -*-
from openerp import fields, models


class ResOrg(models.Model):
    _inherit = 'res.org'

    level_emotion = fields.Many2one(
        'wkf.cmd.level',
        string='Emotion Level',
        help="All level under this level is forced to participate"
        " in workflow, regardless of normal his/her amount limit",
    )
