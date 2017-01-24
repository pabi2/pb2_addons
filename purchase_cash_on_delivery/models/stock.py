# -*- coding: utf-8 -*-
from openerp import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_done(self):
        # Find all POs of all sock move lines, so we can check only once
        purchase_ids = [move.purchase_line_id.order_id.id for move in self]
        purchase_ids = list(set(purchase_ids))
        if False in purchase_ids:
            purchase_ids.remove(False)
        purchases = self.env['purchase.order'].browse(purchase_ids)
        # Validate COD
        purchases._validate_purchase_cod_fully_paid()
        # --
        return super(StockMove, self).action_done()
