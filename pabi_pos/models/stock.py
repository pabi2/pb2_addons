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


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    @api.multi
    def do_enter_transfer_details(self):
        if 'POS' in self.origin:
            #self.validate_picking()
            only_available = self.filtered(
                'workflow_process_id.ship_only_available')
            to_force = self - only_available
            if only_available:
                #only_available.action_assign()
                #only_available.do_prepare_partial()
                only_available.do_transfer()
            if to_force:
                #to_force.force_assign()
                to_force.do_transfer()
        else:
            return super(StockPicking, self).do_enter_transfer_details()


class StockLocation(models.Model):

    _inherit = 'stock.location'

    @api.multi
    def get_current_stock(self, product_names=None):
        Quant = self.env['stock.quant']
        stock = {}
        if product_names is not None:
            product_ids = self.env['product.product'].search([('name', 'in', product_names),
                                                              ('type', '=', 'product')])
            quant_ids = Quant.search([('location_id', 'child_of', self.id),('product_id', 'in', product_ids.ids)])
        else:
            quant_ids = Quant.search([('location_id', 'child_of', self.id)])
            
        product_ids = quant_ids.mapped('product_id')
        for product in product_ids:
            quantity = quant_ids.filtered(lambda l: l.product_id == product)
            stock[product.name] = sum(quantity.mapped('qty'))

        return stock
