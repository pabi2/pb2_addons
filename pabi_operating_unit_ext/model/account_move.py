# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=False,
    )


class AccountMove(models.Model):
    _inherit = "account.move"

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=False,
    )
