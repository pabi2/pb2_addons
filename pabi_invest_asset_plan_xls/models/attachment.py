# -*- coding: utf-8 -*-
from openerp import models, fields


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    invest_asset_plan_id = fields.Many2one(
        'invest.asset.plan',
        string="Invest Asset Plan",
        copy=False,
    )

    def init(self, cr):
        if 'invest.asset.plan' not in self._models_check:
            self._models_check.update(
                {'invest.asset.plan': 'invest_asset_plan_id'})
