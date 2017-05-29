# -*- coding: utf-8 -*-
from openerp import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    asset_ids = fields.One2many(
        'account.asset.asset',
        'picking_id',
        string='Assets',
        readonly=True,
    )
    asset_count = fields.Integer(
        string='Asset Count',
        compute='_compute_assset_count',
    )

    @api.multi
    def action_view_asset(self):
        self.ensure_one()
        Asset = self.env['account.asset.asset']
        action = self.env.ref('account_asset.action_account_asset_asset_form')
        result = action.read()[0]
        assets = Asset.search([('picking_id', '=', self.id)])
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

    parent_asset_id = fields.Many2one(
        'account.asset.asset',
        string='Parent Asset'
    )
    asset_category_id = fields.Many2one(
        'account.asset.category',
        string='Asset Category',
        related='product_id.asset_category_id',
        readonly=True,
        help="Asset Category of this product",
    )

    @api.multi
    def write(self, vals):
        asset_obj = self.env['account.asset.asset']
        Seq = self.env['ir.sequence']
        result = super(StockMove, self).write(vals)
        for move in self:
            if move.state == 'done' and \
                    move.picking_id.picking_type_code == 'incoming' and \
                    move.product_id.asset_category_id:  # Is an asset
                #  Initialization
                date = move.date
                partner_id = False
                if move.purchase_line_id:
                    purchase_value = move.purchase_line_id.price_unit
                    date = move.purchase_line_id.date_planned
                else:
                    purchase_value = move.product_id.standard_price
                # Move of date asset on rely
                if move.picking_id and move.purchase_line_id.order_id and \
                        move.purchase_line_id.order_id.partner_id:
                    partner_id = move.purchase_line_id.order_id.partner_id.id
                elif move.picking_id and move.picking_id.partner_id:
                    partner_id = move.picking_id.partner_id.id
                # Asset
                create_vals = {
                    'name': move.name,
                    'category_id': move.product_id.asset_category_id.id,
                    'purchase_value': purchase_value,
                    'purchase_date': date,
                    'partner_id': partner_id,
                    'product_id': move.product_id.id,
                    'move_id': move.id,
                    'state': 'draft',
                    'parent_id': move.parent_asset_id.id,
                }
                qty = move.product_qty
                while qty > 0:
                    qty -= 1
                    asset_obj.create(create_vals)
        return result
