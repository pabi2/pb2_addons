# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountAssetLine(models.Model):
    _inherit = 'account.asset.line'

    line_days = fields.Integer(
        string='Days',
        readonly=False,
    )


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    owner_section_id = fields.Many2one(
        readonly=False,
    )
    owner_project_id = fields.Many2one(
        readonly=False,
    )
    owner_invest_asset_id = fields.Many2one(
        readonly=False,
    )
    owner_invest_construction_phase_id = fields.Many2one(
        readonly=False,
    )
    purchase_id = fields.Many2one(
        related=False,
        states={'draft': [('readonly', False)]}
    )
