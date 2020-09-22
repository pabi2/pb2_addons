# -*- coding: utf-8 -*-

from openerp import models, fields, api


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.model
    def default_get(self, fields_list):
        res = super(StockTransferDetails, self).default_get(fields_list)
        Acceptance = self.env['purchase.work.acceptance']
        acceptance = self._context.get('acceptance', False)
        if acceptance:
            acceptance_id = Acceptance.browse(acceptance)

        item_ids = res.get('item_ids', False)
        for item_id in item_ids:
            product = item_id.get('product_id', False)
            acceptance_line = acceptance_id and \
                acceptance_id.acceptance_line_ids.filtered(
                    lambda l: l.product_id.id == product)
            item_id['price_unit'] = acceptance_line.price_unit or 0.0
        return res


class StockTransferDetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    price_unit = fields.Float(
        string='Price Unit',
        readonly=True,
    )
