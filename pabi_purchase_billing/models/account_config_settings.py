# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    date_due_day = fields.Char(
        string="Due Date (Days)",
        help="Must be in 1,3, ... format.",
        default="16,28",
        related="company_id.date_due_day",
    )
