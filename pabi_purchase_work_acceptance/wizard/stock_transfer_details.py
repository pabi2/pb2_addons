# -*- coding: utf-8 -*-

from openerp import models, api, _
from openerp.exceptions import Warning as UserError


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.model
    def default_get(self, fields):
        Picking = self.env['stock.picking']
        picking_ids = self.env.context['active_ids'] or []
        picking = Picking.browse(picking_ids)
        res = super(StockTransferDetails, self).default_get(fields)
        if picking.picking_type_code == 'incoming':
            if len(picking.acceptance_id.acceptance_line_ids) == 0:
                raise UserError(
                    _("You have to input Work Acceptance first."))
            new_item_ids = []
            for item in res['item_ids']:
                new_qty = 0
                for wa_line in picking.acceptance_id.acceptance_line_ids:
                    if wa_line.product_id.id == item['product_id']:
                        new_qty += wa_line.to_receive_qty
                item['quantity'] = new_qty
                new_item_ids.append(item)
            res['item_ids'] = new_item_ids
        return res
