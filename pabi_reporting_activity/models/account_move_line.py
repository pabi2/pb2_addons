# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    rpt_activity_id = fields.Many2one(
        'account.activity',
        string='Rpt Activity',
    )
