# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning as UserError, ValidationError


class StockRequest(models.Model):
    _name = 'stock.request'
    _inherit = ['mail.thread']
    _description = "Stock Request"
    _order = "date_request asc, id desc"

    name = fields.Char(
        string='Reference',
        index=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env['res.company'].
        _company_default_get('stock.request')
    )
    type = fields.Selection(
        [('request', 'Request'),
         ('transfer', 'Transfer'),
         ('borrow', 'Borrow')],
        string='Type',
        default='request',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
    )
    date_request = fields.Datetime(
        string='Request Date',
        readonly=True,
    )
    date_approve1 = fields.Datetime(
        string='Date Approve 1',
        readonly=True,
    )
    date_approve2 = fields.Datetime(
        string='Date Approve 2',
        readonly=True,
    )
    date_transfer = fields.Datetime(
        string='Transfer Date',
        readonly=True,
    )
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Type of Operation',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
    )
    location_src_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
    )
    location_dest_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
    )
    transfer_picking_id = fields.Many2one(
        'stock.picking',
        string='Transfer Picking',
        readonly=True,
        ondelete='restrict',
        copy=False,
    )
    return_picking_id = fields.Many2one(
        'stock.picking',
        string='Return Picking',
        readonly=True,
        ondelete='restrict',
        copy=False,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('approve1', 'Waiting Approval 1'),
         ('approve2', 'Waiting Approval 2'),
         ('approved', 'Approved'),
         ('done', 'Transferred'),
         ('cancel', 'Rejected'),
         ],
        readonly=True,
        index=True,
        copy=False,
        default='draft',
    )
    line_ids = fields.One2many(
        'stock.request.line',
        'request_id',
        string='Request Lines',
        readonly=True,
        states={'draft': [('readonly', False)],
                'approve1': [('readonly', False)]},
        copy=True,
    )
    note = fields.Text(
        string='Notes',
    )

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        self.location_src_id = self.picking_type_id.default_location_src_id
        self.location_dest_id = self.picking_type_id.default_location_dest_id

    @api.multi
    def action_to_approve1(self):
        self.write({'date_request': fields.Datetime.now(),
                    'state': 'approve1'})

    @api.multi
    def action_to_approve2(self):
        # Check for availability, if not available, show error
        self.write({'date_approve1': fields.Datetime.now(),
                    'state': 'approve2'})

    @api.multi
    def action_approve(self):
        # Check for availability, if not available, show error
        # Create stock.picking
        picking_id = self.create_picking_and_reserve()
        if picking_id:
            picking = self.env['stock.picking'].browse(picking_id)
            if picking.state != 'assigned':
                raise UserError('Requested material(s) not fully available!')
        else:
            raise UserError('Requested material(s) not of type stockable!')
        self.write({'date_approve2': fields.Datetime.now(),
                    'state': 'approved'})

    @api.multi
    def action_done(self):
        if self.transfer_picking_id:
            self.transfer_picking_id.action_done()
        self.write({'date_transfer': fields.Datetime.now(),
                    'state': 'done'})

    @api.multi
    def action_cancel(self):
        if self.transfer_picking_id:
            self.transfer_picking_id.action_cancel()
        self.write({'state': 'cancel'})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def create_picking_and_reserve(self):
        self.ensure_one()
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        if all(t == 'service'
               for t in self.line_ids.mapped('product_id.type')):
            return False
        partner = self.employee_id.user_id.partner_id
        if not partner:
            raise ValidationError(_('Invalid Employee (no ref partner)'))
        picking_type = self.picking_type_id
        picking = picking_obj.create({
            'origin': self.name,
            'partner_id': partner.id,
            'date_done': self.date_transfer,
            'picking_type_id': picking_type.id,
            'company_id': self.company_id.id,
            'move_type': 'direct',
            'note': self.note or "",
            'invoice_state': 'none',
        })
        self.write({'transfer_picking_id': picking.id})
        location_src_id = self.location_src_id.id
        location_dest_id = self.location_dest_id.id
        for line in self.line_ids:
            if line.product_id and line.product_id.type == 'service':
                continue
            move_obj.create({
                'name': line.product_id.name,
                'product_uom': line.product_uom.id,
                'product_uos': line.product_uom.id,
                'picking_id': picking.id,
                'picking_type_id': picking_type.id,
                'product_id': line.product_id.id,
                'product_uos_qty': abs(line.product_uom_qty),
                'product_uom_qty': abs(line.product_uom_qty),
                'state': 'draft',
                'location_id': location_src_id,
                'location_dest_id': location_dest_id,
            })
            # # If we transfer in picking, this is not necessary
            # # (we have option not to use picking at all.
            # move.action_confirm()
            # move.force_assign()
            # move.action_done()
        picking.action_confirm()
        picking.action_assign()
        return picking.id


class StockRequestLine(models.Model):
    _name = 'stock.request.line'
    _description = 'Stock Request Line'

    request_id = fields.Many2one(
        'stock.request',
        string='Stock Request',
        index=True,
        ondelete='cascade',
        readonly=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        index=True,
        domain=[('type', '<>', 'service')],
    )
    request_uom_qty = fields.Float(
        string='Requested Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        required=True,
        default=1.0,
    )
    product_uom_qty = fields.Float(
        string='Approved Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        required=True,
    )
    product_uom = fields.Many2one(
        'product.uom',
        string='Unit of Measure',
        required=True,
    )
    location_src_id = fields.Many2one(
        'stock.location',
        related='request_id.location_src_id',
        string='Src',
        readonly=True,
    )
    onhand_qty = fields.Float(
        string='Onhand Quantity',
        compute='_compute_product_available',
    )
    future_qty = fields.Float(
        string='Future Quantity',
        compute='_compute_product_available',
    )

    @api.multi
    @api.depends('product_id', 'product_uom', 'location_src_id')
    def _compute_product_available(self):
        for rec in self:
            UOM = self.env['product.uom']
            if rec.product_id:
                qty = rec.product_id.with_context(
                    location=rec.location_src_id.id)._product_available()
                onhand_qty = qty[rec.product_id.id]['qty_available']
                future_qty = qty[rec.product_id.id]['virtual_available']
                rec.onhand_qty = UOM._compute_qty(rec.product_id.uom_id.id,
                                                  onhand_qty,
                                                  rec.product_uom.id)
                rec.future_qty = UOM._compute_qty(rec.product_id.uom_id.id,
                                                  future_qty,
                                                  rec.product_uom.id)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_uom = self.product_id.uom_id

    @api.onchange('request_uom_qty')
    def _onchange_request_uom_qty(self):
        self.product_uom_qty = self.request_uom_qty
