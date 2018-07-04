# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    default_ag_invest_construction_id = fields.Many2one(
        'account.activity.group',
        string='Default Invest Constuction Activity Group',
        related="company_id.default_ag_invest_construction_id",
    )
    default_ag_invest_asset_id = fields.Many2one(
        'account.activity.group',
        string='Default Invest Asset Activity Group',
        related="company_id.default_ag_invest_asset_id",
    )
