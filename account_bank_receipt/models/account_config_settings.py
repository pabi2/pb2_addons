# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    auto_bank_receipt = fields.Boolean(
        string='Auto create Bank Receipt for Customer Payment Intransit',
        related="company_id.auto_bank_receipt",
    )
