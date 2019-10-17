# -*- coding: utf-8 -*-
from openerp import models, api, fields, _


class Inventory(models.Model):
    _inherit = 'stock.inventory'

    stock_move_related_count = fields.Integer(
        string='# of Invoices',
        compute='_compute_stock_move_related_count',
        help='Count invoice in billing',
    )

    @api.multi
    def _compute_stock_move_related_count(self):
        for inventory in self:
            move_ids = self.env['stock.move'].search_count([
                ('id', 'in', inventory.move_ids.ids)
            ])
            inventory.stock_move_related_count = move_ids

    @api.multi
    def stock_move_tree_view(self):
        self.ensure_one()
        action = self.env.ref('stock.action_move_form2')
        result = action.read()[0]
        result.update({'domain': [('id', 'in', self.move_ids.ids)]})
        return result


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    @api.model
    def _get_move_values(
            self, inventory_line, qty, location_id, location_dest_id):
        res = super(StockInventoryLine, self)._get_move_values(
            inventory_line, qty, location_id, location_dest_id)
        res['name'] = inventory_line.product_id.name
        # TODO: Fix this
        res['origin'] = _('INV:') + (inventory_line.inventory_id.name or '')
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    account_move_id = fields.Many2one(
        comodel_name='account.move',
        string='Journal Entry',
        help='Account Move',
    )
