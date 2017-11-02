# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    investment_id = fields.Many2one(
        'res.partner.investment',
        string='Investment',
        index=True,
        ondelete='restrict',
    )
