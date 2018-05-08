# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    no_partner_tag_change_account = fields.Boolean(
        string="Disallow changing of Partner's Tag, "
               "when it result in changing account code for that partner",
        related="company_id.no_partner_tag_change_account",
    )
