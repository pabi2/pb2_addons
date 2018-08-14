# -*- coding: utf-8 -*-
from openerp import models, fields, api
from ..models.chartfield import ChartFieldAction


class StockChangeProductQty(ChartFieldAction, models.TransientModel):
    _inherit = 'stock.change.product.qty'

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
        res = super(StockChangeProductQty, self).create(vals)
        res.update_related_dimension(vals)
        return res

    @api.model
    def _prepare_inventory_line(self, inventory_id, data):
        res = super(StockChangeProductQty, self)._prepare_inventory_line(
            inventory_id, data)
        res.update({'activity_group_id': data.activity_group_id.id,
                    'activity_rpt_id': data.activity_rpt_id.id,
                    'project_id': data.project_id.id,
                    'section_id': data.section_id.id,
                    'fund_id': data.fund_id.id, })
        return res
