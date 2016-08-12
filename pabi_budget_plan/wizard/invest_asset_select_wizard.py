# -*- coding: utf-8 -*-
from openerp import api, models, fields


class InvestAssetSelect(models.TransientModel):
    _name = "invest.asset.selection.wiz"

    select = fields.Boolean(
        string='Select',
        default=True,
    )
    invest_plan_id = fields.Many2one(
        'invest.asset.plan',
        'Invest Plan',
        readonly=True,
    )
    asset_line_ids = fields.Many2many(
        'invest.asset.plan.item',
        'invest_asset_plan_invest_asset_selection_wiz_rel',
        string='Asset Lines',
    )

    @api.multi
    def update_asset_lines(self):
        self.ensure_one()
        self.asset_line_ids.write({'select': self.select})
