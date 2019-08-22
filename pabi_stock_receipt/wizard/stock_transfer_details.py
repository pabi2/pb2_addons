# -*- coding: utf-8 -*-

from openerp import models, api, _
from openerp.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.one
    def do_detailed_transfer(self):
        _logger.info("pabi_stock_receipt/wizard/stock_transfer_details")
        skip_wa = self._context.get('skip_work_acceptance', False) or \
            self._context.get('order_type') == 'sale_order'  # No WA in SO
        picking = self.picking_id
        if picking.picking_type_code == 'incoming' and not skip_wa:
            transfer_qty = self._product_summary_qty(self.item_ids,
                                                     'quantity')
            wa_qty = self._product_summary_qty(picking.acceptance_id.
                                               acceptance_line_ids,
                                               'to_receive_qty')
            product_lists = []
            for item in self.item_ids:
                product_lists.append(item.product_id.id)
            list_dup_product_ids = list(
                set([x for x in product_lists if product_lists.count(x) > 1])
            )

            # Check multi line product receiving qty
            for dup_prod in list_dup_product_ids:
                if dup_prod in wa_qty and dup_prod in transfer_qty:
                    if wa_qty[dup_prod] > transfer_qty[dup_prod]:
                        raise ValidationError(
                            _(
                                "Can't process partial multi duplicate "
                                "product line.You have to fully receipt "
                                "the product."
                            )
                        )

        res = super(StockTransferDetails, self).do_detailed_transfer()
        return res
