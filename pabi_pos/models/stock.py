# -*- coding: utf-8 -*-
from openerp import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _picking_assign(self, procurement_group, location_from, location_to):
        res = super(StockMove, self)._picking_assign(procurement_group,
                                                     location_from,
                                                     location_to)
        pickings = self.mapped('picking_id')
        for picking in pickings:
            if picking.workflow_process_id:
                picking.move_lines.write({
                    'location_id': picking.workflow_process_id.location_id.id})
        return res
