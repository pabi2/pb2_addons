# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.model
    def default_get(self, fields):
        Picking = self.env['stock.picking']
        picking_ids = self.env.context['active_ids'] or []
        picking = Picking.browse(picking_ids)
        res = super(StockTransferDetails, self).default_get(fields)
        skip_wa = self._context.get('skip_work_acceptance', False)
        if picking.picking_type_code == 'incoming' and not skip_wa and \
                not picking.move_lines.filtered('origin_returned_move_id'):
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

    @api.model
    def _product_summary_qty(self, product_lines, qty_field):
        summary_qty = {}
        products = product_lines.mapped('product_id')
        for product in products:
            lines = product_lines.filtered(lambda l:
                                           l.product_id.id == product.id)
            summary_qty[product.id] = sum(lines.mapped(qty_field))
        return summary_qty

    @api.one
    def do_detailed_transfer(self):
        skip_wa = self._context.get('skip_work_acceptance', False) or \
            self._context.get('order_type') == 'sale_order'  # No WA in SO
        picking = self.picking_id
        if picking.picking_type_code == 'incoming' and not skip_wa:
            transfer_qty = self._product_summary_qty(self.item_ids,
                                                     'quantity')
            stock_move_qty = self._product_summary_qty(picking.move_lines,
                                                       'product_uom_qty')
            wa_qty = self._product_summary_qty(picking.acceptance_id.
                                               acceptance_line_ids,
                                               'to_receive_qty')
            # Check transfer with WA
            for product_id, quantity in transfer_qty.items():
                if product_id not in wa_qty or \
                        float_compare(quantity, wa_qty[product_id], 2) == 1:
                    raise ValidationError(
                        _("Can't receive product's quantity over "
                          "work acceptance's quantity.")
                    )
            # Check transfer with picking line
            for product_id, quantity in transfer_qty.items():
                if product_id not in stock_move_qty or \
                        quantity > stock_move_qty[product_id]:
                    raise ValidationError(
                        _("Can't receive product's quantity over "
                          "stock move's quantity.")
                    )
            # Stamp WA accept date
            picking.acceptance_id.date_accept = fields.Date.context_today(self)
        res = super(StockTransferDetails, self).do_detailed_transfer()
        return res
