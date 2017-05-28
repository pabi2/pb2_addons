# -*- coding: utf-8 -*-

from openerp import models, api, _
from openerp.exceptions import ValidationError


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
                raise ValidationError(
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

    @api.one
    def do_detailed_transfer(self):
        picking = self.picking_id
        if picking.picking_type_code == 'incoming':
            # Build product: quantity list for transfer wizard
            incoming_qty = {}
            products = self.item_ids.mapped('product_id')
            for product in products:
                lines = self.item_ids.filtered(lambda l:
                                               l.product_id.id == product.id)
                incoming_qty[product.id] = sum(lines.mapped('quantity'))
            # Build product: quantity list for WA
            wa_qty = {}
            wa_lines = picking.acceptance_id.acceptance_line_ids
            products = wa_lines.mapped('product_id')
            for product in products:
                lines = wa_lines.filtered(lambda l:
                                          l.product_id.id == product.id)
                wa_qty[product.id] = sum(lines.mapped('to_receive_qty'))
            # Check incoming with WA
            print incoming_qty
            print wa_qty
            for product_id, quantity in incoming_qty.items():
                if product_id not in wa_qty:
                    raise ValidationError(
                        _('Product not in work acceptance list.'))
                if quantity > wa_qty[product.id]:
                    raise ValidationError(
                        _("Can't receive product's quantity over than "
                          "work acceptance's quantity.")
                    )
        res = super(StockTransferDetails, self).do_detailed_transfer()
        return res
