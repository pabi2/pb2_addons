# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    line_item_summary = fields.Text(
        compute=False,
    )
