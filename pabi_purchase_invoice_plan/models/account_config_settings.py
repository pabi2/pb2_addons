# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    other_deposit_account_ids = fields.Many2many(
        'account.account',
        string='Other Advance Accounts',
        related='company_id.other_deposit_account_ids',
        help="Lst other eligible for user to choose manually on document",
    )
