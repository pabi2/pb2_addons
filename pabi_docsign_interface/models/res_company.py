# -*- coding: utf-8 -*-
# © 2020 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    # e-Tax
    pabietax_active = fields.Boolean(
        string='Open Connection to e-Tax Webservice',
        size=500,
    )
    pabietax_web_url = fields.Char(
        string='e-Tax Web URL',
    )
    pabietax_db = fields.Char(
        string='e-Tax Database',
    )
    pabietax_user = fields.Char(
        string='e-Tax Login',
        size=500,
    )
    pabietax_password = fields.Char(
        string='e-Tax Password',
        size=500,
    )
