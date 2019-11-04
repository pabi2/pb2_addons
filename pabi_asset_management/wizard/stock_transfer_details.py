# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.model
    def _asset_split_line(self, res):
        Product = self.env['product.product']
        new_items = []
        for item in res['item_ids']:
            quantity = item['quantity']
            if quantity <= 1:  # For qty = 1, no need to split
                new_items.append(item)
                continue
            product = Product.browse(item['product_id'])
            # Only case asset, force split
            if product.valuation == 'real_time' and product.asset:
                item['quantity'] = 1
                item['packop_id'] = False
                while quantity > 0:
                    new_item = item.copy()
                    new_items.append(new_item)
                    quantity -= 1
            else:
                new_items.append(item)
        return new_items

    @api.model
    def default_get(self, fields):
        res = super(StockTransferDetails, self).default_get(fields)
        res['item_ids'] = self._asset_split_line(res)
        return res

    @api.multi
    def _validate_asset_line(self):
        for rec in self:
            for line in rec.item_ids:
                if line.product_id.asset and line.quantity and \
                        not line.quantity.is_integer():
                    raise ValidationError(_('For asset, quantity '
                                            'must be whole number.'))
        return True

    @api.multi
    def do_detailed_transfer(self):
        self.ensure_one()
        self._validate_asset_line()
        # Pass Installament information to Asset
        wa = self.picking_id.acceptance_id
        if wa:
            self = self.with_context({'work_acceptance_id': wa.id,
                                      'installment': wa.installment,
                                      'num_installment': wa.num_installment})
        _logger.info("self.id: %s", str(self.id))
        _logger.info("self.asset_ids: %s", str(self.asset_ids))
        _logger.info("self._context: %s", str(self._context))
        res = super(StockTransferDetails, self).do_detailed_transfer()
        _logger.info("res: %s", str(res))
        return res
