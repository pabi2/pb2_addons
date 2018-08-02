# -*- coding: utf-8 -*-
from openerp import models, fields, api
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

    # Using ActivityCommon got error on copy. So, we do it manually for now.
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_rpt_id = fields.Many2one(
        'account.activity',
        string='Activity',
        domain="[('activity_group_ids', 'in', activity_group_id)]",
    )

    @api.onchange('activity_group_id')
    def _onchange_activity_group_id(self):
        self.activity_rpt_id = False

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
        data.update({'activity_group_id': inventory_line.activity_group_id.id,
                     'activity_rpt_id': inventory_line.activity_rpt_id.id,
                     'project_id': inventory_line.project_id.id,
                     'section_id': inventory_line.section_id.id,
                     'fund_id': inventory_line.fund_id.id,
                     })
        return data
