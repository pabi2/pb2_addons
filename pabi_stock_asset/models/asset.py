# -*- coding: utf-8 -*-

from openerp import models, fields, api


class StockMove(models.Model):

    _inherit = 'stock.move'

    parent_asset_id = fields.Many2one(
        'account.asset.asset',
        string='Parent Asset'
    )

    @api.model
    def _assign_lot_to_asset(self):
        parent = []
        Seq = self.env['ir.sequence']
        Lot = self.env['stock.production.lot']
        for item in self.item_ids:
            if item.product_id.sequence_id and item.product_id.financial_asset:
                new_seq = Seq.get(item.product_id.sequence_id.code)
                new_lot = Lot.create({
                    'name': new_seq,
                    'product_id': item.product_id.id,
                })
                item.lot_id = new_lot.id
                if item.parent_asset_id:
                    parent.append(
                        (new_lot.id, item.parent_asset_id.id or False),
                    )
        return parent

    @api.multi
    def write(self, vals):
        asset_obj = self.env['account.asset.asset']

        result = super(StockMove, self).write(vals)
        for move in self:
            if move.state == 'done' and \
                move.generate_asset and \
                    move.product_id.financial_asset:
                write_vals = {
                    'name': move.name or move.product_id.name,
                    'parent_id': move.parent_asset_id.id or False,
                }
                asset_ids = asset_obj.search(
                    [('move_id', '=', move.id)], limit=1)
                asset_ids.write(write_vals)
        return result
