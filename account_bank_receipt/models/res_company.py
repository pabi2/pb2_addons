# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    auto_bank_receipt = fields.Boolean(
        string='Auto create Bank Receipt for Customer Payment Intransit',
        default=False,
    )
