# -*- coding: utf-8 -*-
# © 2020 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class PABIWebConfigSettings(models.TransientModel):
    _inherit = 'pabi.web.config.settings'

    # e-Tax
    pabietax_active = fields.Boolean(
        string='Open Connection to e-Tax Webservice',
        related='company_id.pabietax_active',
    )
    pabietax_web_url = fields.Char(
        string='e-Tax Web URL',
        related='company_id.pabietax_web_url',
    )
    pabietax_db = fields.Char(
        string='e-Tax Database',
        related='company_id.pabietax_db',
    )
    pabietax_user = fields.Char(
        string='e-Tax Login',
        related='company_id.pabietax_user',
    )
    pabietax_password = fields.Char(
        string='e-Tax Password',
        related='company_id.pabietax_password',
    )
