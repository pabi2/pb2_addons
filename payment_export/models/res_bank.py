# -*- coding: utf-8 -*-
from openerp import fields, models


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    owner_name_en = fields.Char(
        'Account Owner Name En'
    )
    register_no = fields.Char(
        'Register No.'
    )
    register_date = fields.Date(
        'Register date'
    )
    is_register = fields.Boolean(
        'Is Register'
    )

