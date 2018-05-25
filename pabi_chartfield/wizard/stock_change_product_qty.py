# -*- coding: utf-8 -*-
from openerp import models, api
from ..models.chartfield import ChartFieldAction


class StockChangeProductQty(ChartFieldAction, models.TransientModel):
    _inherit = 'stock.change.product.qty'

    @api.model
    def create(self, vals):
        res = super(StockChangeProductQty, self).create(vals)
        res.update_related_dimension(vals)
        return res

    @api.model
    def _prepare_inventory_line(self, inventory_id, data):
        res = super(StockChangeProductQty, self)._prepare_inventory_line(
            inventory_id, data)
        res.update({'project_id': data.project_id.id,
                    'section_id': data.section_id.id,
                    'fund_id': data.fund_id.id, })
        return res
