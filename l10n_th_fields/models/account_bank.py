# -*- coding: utf-8 -*-
from openerp import models, fields


class Bank(models.Model):
    _inherit = "res.partner.bank"

    bank_branch = fields.Char(
        string='Bank Branch',
        size=64,
    )
