# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    no_partner_tag_change_account = fields.Boolean(
        string="Disallow changing of Partner's Tag, "
               "when it result in changing account code for that partner",
        default=False,
    )
    default_employee_partner_categ_id = fields.Many2one(
        'res.partner.category',
        string="Default employee's partner category",
        help="To be used when partner is auto created by creating new user"
    )
