# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    cancel_entry = fields.Boolean(
        string='Cancelled Entry',
        default=False,
    )
