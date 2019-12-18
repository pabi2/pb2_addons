# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


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
            for line in self.move_lines:
                if line.product_uom_qty > \
                        sum(line.reserved_quant_ids.mapped('qty')):
                    raise ValidationError(
                        _('%s don\'t have enough quantity')
                        % line.product_id.name)
            # self.validate_picking()
            only_available = self.filtered(
                'workflow_process_id.ship_only_available')
            to_force = self - only_available
            if only_available:
                # only_available.action_assign()
                # only_available.do_prepare_partial()
                only_available.do_transfer()
            if to_force:
                # to_force.force_assign()
                to_force.do_transfer()
        else:
            return super(StockPicking, self).do_enter_transfer_details()
