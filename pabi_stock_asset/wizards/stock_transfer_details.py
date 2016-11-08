# -*- coding: utf-8 -*-

from openerp import models,  api


class StockTransferDetails(models.TransientModel):

    _inherit = 'stock.transfer_details'

    @api.one
    def do_detailed_transfer(self):
        res = super(StockTransferDetails, self).do_detailed_transfer()
        return res
