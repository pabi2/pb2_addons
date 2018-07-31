# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    default_ag_invest_construction_id = fields.Many2one(
        'account.activity.group',
        string='Default Invest Constuction Activity Group',
    )
    default_ag_invest_asset_id = fields.Many2one(
        'account.activity.group',
        string='Default Invest Asset Activity Group',
    )
