# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    auto_bank_payment = fields.Boolean(
        string='Auto create Bank Payment for Supplier Payment Intransit',
        default=False,
    )
