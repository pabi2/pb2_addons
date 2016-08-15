# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseRequisitionPartner(models.TransientModel):
    _inherit = "purchase.requisition.partner"

    is_central_purchase = fields.Boolean(
        string='Central Purchase',
        default=lambda self: self.env['purchase.requisition'].
        browse(self._context.get('active_id')).is_central_purchase
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Picking Type',
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
    )

    @api.multi
    def create_order(self):
        return super(PurchaseRequisitionPartner,
                     self.with_context(
                         sel_operating_unit_id=self.operating_unit_id.id,
                         sel_picking_type_id=self.picking_type_id.id,
                         sel_location_id=self.location_id.id)).\
            create_order()

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        type_obj = self.env['stock.picking.type']
        if self.operating_unit_id:
            types = type_obj.search([('code', '=', 'incoming'),
                                     ('warehouse_id.operating_unit_id', '=',
                                      self.operating_unit_id.id)])
            if types:
                self.picking_type_id = types[:1]
                res = self.env['purchase.order'].\
                    onchange_picking_type_id(self.picking_type_id.id)
                self.location_id = res['value']['location_id']
            else:
                raise Warning(_("No Warehouse found with the "
                                "Operating Unit indicated in the "
                                "Purchase Requisition!"))
