# -*- coding: utf-8 -*-
from openerp import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    asset_ids = fields.One2many(
        'account.asset',
        'picking_id',
        string='Assets',
        readonly=True,
    )
    asset_count = fields.Integer(
        string='Asset Count',
        compute='_compute_assset_count',
    )
    asset_purchase_method_id = fields.Many2one(
        'asset.purchase.method',
        string='Aquisition Method',
        help="In case of direct receive, user will manually choose it."
    )

    @api.multi
    def action_view_asset(self):
        self.ensure_one()
        Asset = self.env['account.asset']
        action = self.env.ref('account_asset_management.account_asset_action')
        result = action.read()[0]
        assets = Asset.with_context(active_test=False).search([('picking_id',
                                                                '=', self.id)])
        dom = [('id', 'in', assets.ids)]
        result.update({'domain': dom})
        return result

    @api.multi
    @api.depends()
    def _compute_assset_count(self):
        for rec in self:
            rec.asset_count = len(rec.asset_ids)


class StockMove(models.Model):
    _inherit = 'stock.move'

    asset_value = fields.Float(
        string='Asset Value (each)',
        help="Case direct receive, need to spcifiy asset value",
    )
