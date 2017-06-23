# -*- coding: utf-8 -*-
from openerp import models, fields


class ResProject(models.Model):
    _inherit = 'res.project'

    asset_ids = fields.One2many(
        'account.asset',
        'owner_project_id',
        string='Assets',
    )
