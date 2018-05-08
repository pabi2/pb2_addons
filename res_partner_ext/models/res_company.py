# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    no_partner_tag_change_account = fields.Boolean(
        string="Disallow changing of Partner's Tag, "
               "when it result in changing account code for that partner",
        default=False,
    )
