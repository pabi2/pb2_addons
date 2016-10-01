# -*- coding: utf-8 -*-

from openerp import models, fields, api


class StockTransferDetails(models.TransientModel):

    _inherit = 'stock.transfer_details'

    @api.model
    def _assign_lot_to_asset(self):
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

    @api.one
    def do_detailed_transfer(self):
        self._assign_lot_to_asset()
        res = super(StockTransferDetails, self).do_detailed_transfer()
        return res
