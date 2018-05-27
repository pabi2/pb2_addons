# -*- coding: utf-8 -*-
from openerp import models, api
from .chartfield import ChartFieldAction


class StockMove(ChartFieldAction, models.Model):
    _inherit = 'stock.move'

    @api.model
    def create(self, vals):
        res = super(StockMove, self).create(vals)
        res.update_related_dimension(vals)
        return res


class StockInventoryLine(ChartFieldAction, models.Model):
    _inherit = 'stock.inventory.line'

    @api.model
    def create(self, vals):
        res = super(StockInventoryLine, self).create(vals)
        res.update_related_dimension(vals)
        return res

    @api.model
    def _get_move_values(self, inventory_line, qty,
                         location_id, location_dest_id):
        data = super(StockInventoryLine, self)._get_move_values(
            inventory_line, qty, location_id, location_dest_id)
        data.update({'project_id': inventory_line.project_id.id,
                     'section_id': inventory_line.section_id.id,
                     'fund_id': inventory_line.fund_id.id,
                     })
        return data
