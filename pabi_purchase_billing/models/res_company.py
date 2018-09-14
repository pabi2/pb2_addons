# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    date_due_day = fields.Char(
        string="Due Date Configuration",
        default="16,28",
        size=10,
    )
