# -*- coding: utf-8 -*-

from openerp import models, fields


class StockTransferDetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    price_unit = fields.Float(
        string='Price Unit',
        readonly=True,
    )
