# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class PurchaseRequisitionPartner(models.TransientModel):
    _inherit = "purchase.requisition.partner"

    is_central_purchase = fields.Boolean(
        string='Central Purchase',
        default=lambda self: self.env['purchase.requisition'].
        browse(self._context.get('active_id')).is_central_purchase
    )
    operating_unit_view_id = fields.Many2one(
        'operating.unit.view',
        string='Operating Unit',
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        compute='_compute_operating_unit_id',
    )
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Picking Type',
        compute='_compute_operating_unit_id',
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        compute='_compute_operating_unit_id',
    )

    @api.one
    @api.depends('operating_unit_view_id')
    def _compute_operating_unit_id(self):
        if self.operating_unit_view_id:
            self.operating_unit_id = self.operating_unit_view_id.id
            type_obj = self.env['stock.picking.type'].sudo()
            types = type_obj.search(
                [('code', '=', 'incoming'),
                 ('warehouse_id.operating_unit_id', '=',
                  self.operating_unit_view_id.id)])
            if types:
                self.picking_type_id = types[0]
                self.location_id = types[0].default_location_dest_id

    @api.multi
    def create_order(self):
        if self._context['active_model'] == 'purchase.requisition':
            Requisition = self.env['purchase.requisition']
            requisitions = Requisition.browse(self._context['active_ids'])
            for req in requisitions:
                if not req.request_ref_id and req.state == 'in_progress':
                    raise ValidationError(
                        _("Allowed for PR Referred CfB only.")
                    )
        res = super(PurchaseRequisitionPartner, self.with_context(
            sel_operating_unit_id=self.operating_unit_view_id.id,
            sel_picking_type_id=self.sudo().picking_type_id.id,
            sel_location_id=self.sudo().location_id.id,
            order_type='quotation').sudo(),
        ).create_order()
        return res
