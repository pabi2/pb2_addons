# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.model
    def default_get(self, field_list):
        res = super(StockTransferDetails, self).default_get(field_list)
        print res
        # if context is None: context = {}
        # res = super(stock_transfer_details, self).default_get(cr, uid, fields, context=context)
        # picking_ids = context.get('active_ids', [])
        # active_model = context.get('active_model')
        #
        # if not picking_ids or len(picking_ids) != 1:
        #     # Partial Picking Processing may only be done for one picking at a time
        #     return res
        # assert active_model in ('stock.picking'), 'Bad context propagation'
        # picking_id, = picking_ids
        # picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
        # items = []
        # packs = []
        # if not picking.pack_operation_ids:
        #     picking.do_prepare_partial()
        # for op in picking.pack_operation_ids:
        #     item = {
        #         'packop_id': op.id,
        #         'product_id': op.product_id.id,
        #         'product_uom_id': op.product_uom_id.id,
        #         'quantity': op.product_qty,
        #         'package_id': op.package_id.id,
        #         'lot_id': op.lot_id.id,
        #         'sourceloc_id': op.location_id.id,
        #         'destinationloc_id': op.location_dest_id.id,
        #         'result_package_id': op.result_package_id.id,
        #         'date': op.date,
        #         'owner_id': op.owner_id.id,
        #     }
        #     if op.product_id:
        #         items.append(item)
        #     elif op.package_id:
        #         packs.append(item)
        # res.update(item_ids=items)
        # res.update(packop_ids=packs)
        return res


class StockTransferDetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    name = fields.Char(
        string='Description',
        size=100,
    )
    price_unit = fields.Float(
        string='Price Unit',
    )
