# -*- coding: utf-8 -*-
from lxml import etree
from openerp import models, api, fields, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning as UserError, ValidationError


class StockRequest(models.Model):
    _name = 'stock.request'
    _inherit = ['mail.thread']
    _description = "Stock Request"
    _order = "date_request asc, id desc"

    _STATES = [('draft', 'Draft'),
               ('approve1', 'Waiting Approval 1'),
               ('approve2', 'Waiting Approval 2'),
               ('approved', 'Approved'),
               ('done', 'Transferred'),
               ('done_return', 'Returned'),
               ('cancel', 'Rejected'),
               ]

    name = fields.Char(
        string='Number',
        index=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        required=True,
        default='/',
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
        default=lambda self: self.env['hr.employee'].
        search([('user_id', '=', self._uid)]),
    )
    date_request = fields.Datetime(
        string='Request Date',
        readonly=True,
        copy=False,
    )
    date_approve1 = fields.Datetime(
        string='Date Approve 1',
        readonly=True,
        copy=False,
    )
    date_approve2 = fields.Datetime(
        string='Date Approve 2',
        readonly=True,
        copy=False,
    )
    date_transfer = fields.Datetime(
        string='Transfer Date',
        readonly=True,
        copy=False,
    )
    date_return = fields.Datetime(
        string='Return Date',
        readonly=True,
        copy=False,
    )
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Type of Operation',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
        domain=[('code', '=', 'internal')],
    )
    location_src_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
        domain=[('usage', '=', 'internal')],
    )
    location_dest_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
        domain=[('usage', '=', 'internal')],
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
        _STATES,
        string='Status',
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

    @api.one
    @api.constrains('location_src_id', 'location_dest_id')
    def _check_location(self):
        if self.location_dest_id == self.location_src_id:
            raise UserError(_('Source and Destination Location '
                              'can not be the same location'))

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        res = super(StockRequest, self).\
            fields_view_get(view_id=view_id, view_type=view_type,
                            toolbar=toolbar, submenu=submenu)
        if self._context.get('default_type') == 'borrow':
            res['arch'] = res['arch'].replace(
                'visible="draft,approve1,approve2,approved,done"',
                'visible="draft,approve1,approve2,approved,done,done_return"')
        return res

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            stype = vals.get('type', False)
            code = (stype == 'request' and 'stock.request') or \
                (stype == 'transfer' and 'stock.transfer') or \
                (stype == 'borrow' and 'stock.borrow') or False
            vals['name'] = self.env['ir.sequence'].get(code) or '/'
        return super(StockRequest, self).create(vals)

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        self.location_src_id = self.picking_type_id.default_location_src_id
        self.location_dest_id = self.picking_type_id.default_location_dest_id

    @api.multi
    def action_to_approve1(self):
        self.ensure_one()
        self.write({'date_request': fields.Datetime.now(),
                    'state': 'approve1'})

    @api.multi
    def action_to_approve2(self):
        self.ensure_one()
        # Check for availability, if not available, show error
        self.write({'date_approve1': fields.Datetime.now(),
                    'state': 'approve2'})

    @api.multi
    def action_approve(self):
        self.ensure_one()
        self.create_picking('transfer')  # Create
        self.transfer_picking_id.action_confirm()  # Confirm and reserve
        self.transfer_picking_id.action_assign()
        if self.transfer_picking_id.state != 'assigned':
            raise UserError('Requested material(s) not fully available!')
        self.write({'date_approve2': fields.Datetime.now(),
                    'state': 'approved'})

    @api.multi
    def action_done(self):
        self.ensure_one()
        if self.transfer_picking_id:
            self.transfer_picking_id.action_done()
        self.write({'date_transfer': fields.Datetime.now(),
                    'state': 'done'})
        if self.type == 'borrow':  # prepare for return
            self.create_picking('return')

    @api.multi
    def action_return(self):
        self.ensure_one()
        if self.return_picking_id:
            self.return_picking_id.action_confirm()
            self.return_picking_id.action_assign()
            if self.return_picking_id.state != 'assigned':
                raise UserError('Requested material(s) not fully available!')
            self.return_picking_id.action_done()
        self.write({'date_return': fields.Datetime.now(),
                    'state': 'done_return'})

    @api.multi
    def action_cancel(self):
        self.ensure_one()
        if self.transfer_picking_id:
            self.transfer_picking_id.action_cancel()
        self.write({'state': 'cancel'})

    @api.multi
    def action_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})

    @api.model
    def _prepare_picking(self, request):
        partner = request.employee_id.user_id.partner_id
        if not partner:
            raise ValidationError(_('Invalid Employee (no ref partner)'))
        data = {
            'origin': request.name,
            'partner_id': partner.id,
            'date_done': request.date_transfer,
            'picking_type_id': request.picking_type_id.id,
            'company_id': request.company_id.id,
            'move_type': 'direct',
            'note': request.note or "",
            'invoice_state': 'none',
        }
        return data

    @api.model
    def _prepare_picking_line(self, line, picking,
                              location_src_id,
                              location_dest_id):
        data = {
            'name': line.product_id.name,
            'product_uom': line.product_uom.id,
            'product_uos': line.product_uom.id,
            'picking_id': picking.id,
            'picking_type_id': picking.picking_type_id.id,
            'product_id': line.product_id.id,
            'product_uos_qty': abs(line.product_uom_qty),
            'product_uom_qty': abs(line.product_uom_qty),
            'state': 'draft',
            'location_id': location_src_id,
            'location_dest_id': location_dest_id,
        }
        return data

    @api.multi
    def create_picking(self, ttype):
        self.ensure_one()
        if ttype not in ('transfer', 'return'):
            raise ValidationError(_('Invalid picking type!'))
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        if all(t == 'service'
               for t in self.line_ids.mapped('product_id.type')):
            raise UserError('Requested material(s) not of type stockable!')
        picking = picking_obj.create(self._prepare_picking(self))
        location_src_id = False
        location_dest_id = False
        if ttype == 'transfer':
            self.write({'transfer_picking_id': picking.id})
            location_src_id = self.location_src_id.id
            location_dest_id = self.location_dest_id.id
        elif ttype == 'return':
            self.write({'return_picking_id': picking.id})
            location_dest_id = self.location_src_id.id
            location_src_id = self.location_dest_id.id
        for line in self.line_ids:
            if line.product_id and line.product_id.type == 'service':
                continue
            move_obj.create(self._prepare_picking_line(line, picking,
                                                       location_src_id,
                                                       location_dest_id))
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
