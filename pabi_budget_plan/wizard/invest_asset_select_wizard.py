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
    invset_asset_wiz_line_ids = fields.One2many(
        'invest.asset.selection.wiz.line',
        'invest_asset_wiz_id',
        string="Invest Asset Plan Items"
    )

    @api.model
    def default_get(self, fields):
        res = super(InvestAssetSelect, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        InvestAssetPlan = self.env[active_model].browse(active_id)
        res['invset_asset_wiz_line_ids'] = []
        for item in InvestAssetPlan.item_ids:
            vals = {
                'invest_asset_plan_item_id': item.id,
                'select': item.select,
                'section_id': item.section_id.id,
                'division_id': item.division_id.id,
                'priority':  item.priority,
                'quantity': item.quantity,
                'price_total': item.price_total,
            }
            res['invset_asset_wiz_line_ids'].append((0, 0, vals))
        return res

    @api.multi
    def update_asset_lines(self):
        self.ensure_one()
        for line in self.invset_asset_wiz_line_ids:
            line.invest_asset_plan_item_id.select = line.select


class InvestAssetSelectLine(models.TransientModel):
    _name = "invest.asset.selection.wiz.line"

    select = fields.Boolean(
        string='Select',
        default=True,
    )
    invest_asset_wiz_id = fields.Many2one(
        'invest.asset.selection.wiz',
        string='Invest Asset Selection'
    )
    invest_asset_plan_item_id = fields.Many2one(
        'invest.asset.plan.item',
        string='Invest Asset Plan Items',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        readonly=True,
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
        readonly=True,
    )
    priority = fields.Integer(
        string='Priority',
        readonly=True,
    )
    quantity = fields.Float(
        string='Quantity',
        readonly=True,
    )
    price_total = fields.Float(
        string='Price Total',
        readonly=True,
    )
