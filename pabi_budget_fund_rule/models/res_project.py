# -*- coding: utf-8 -*-
from openerp import models, fields


class ResProject(models.Model):
    _inherit = 'res.project'

    require_fund_rule = fields.Boolean(
        string='Require Fund Rule',
        default=False,
        help="If checked, a fund rule must be created for this project/fund",
    )
