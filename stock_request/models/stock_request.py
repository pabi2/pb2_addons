# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError


_STATES = [
    ('draft', 'Draft'),
    ('wait_confirm', 'Waiting for Confirmation'),
    ('confirmed', 'Confirmed'),
    ('wait_approve', 'Waiting for Approval'),
    ('approved', 'Approved'),
    ('ready', 'Ready to Transfer'),
    ('done', 'Transferred'),
    ('done_return', 'Returned'),
    ('cancel', 'Rejected'),
]


class StockRequest(models.Model):
    _name = 'stock.request'
    _inherit = ['mail.thread']
    _description = "Stock Request"
    _order = "id desc"

    name = fields.Char(
        string='Number',
        index=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        required=True,
        default='/',
        copy=False,
        size=500,
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
        string='Requester',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
        default=lambda self: self.env['hr.employee'].
        search([('user_id', '=', self._uid)]),
    )
    supervisor_emp_id = fields.Many2one(
        'hr.employee',
        string="Requester's Supervisor",
        readonly=True,
        compute='_compute_supervisor_emp_id',
        store=True,
    )
    prepare_emp_id = fields.Many2one(
        'hr.employee',
        string='Preparer',
        required=True,
        readonly=True,
        default=lambda self: self.env['hr.employee'].
        search([('user_id', '=', self._uid)]),
    )
    receive_emp_id = fields.Many2one(
        'hr.employee',
        string='Receiver',
        required=False,
        readonly=False,
        states={'done': [('readonly', True)],
                'done_return': [('readonly', True)],
                'cancel': [('readonly', True)]},
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
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
        domain=[('usage', '=', 'internal'), ('for_stock_request', '=', True)],
    )
    location_dest_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
        domain=[('usage', '=', 'internal'), ('for_stock_request', '=', True)],
    )
    location_borrow_id = fields.Many2one(
        'stock.location',
        string='Borrow from Location',
        required=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
        domain=[('usage', '=', 'internal'), ('for_stock_request', '=', True)],
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
        track_visibility='always',
    )
    line_ids = fields.One2many(
        'stock.request.line',
        'request_id',
        string='Request Lines',
        readonly=True,
        states={'draft': [('readonly', False)],
                'wait_confirm': [('readonly', False)],
                'confirmed': [('readonly', False)],
                'wait_approve': [('readonly', False)]},
        copy=True,
    )
    line2_ids = fields.One2many(
        'stock.request.line',
        'request_id',
        string='Request Lines',
        readonly=True,
        states={'draft': [('readonly', False)],
                'wait_confirm': [('readonly', False)],
                'confirmed': [('readonly', False)],
                'wait_approve': [('readonly', False)]},
        copy=True,
        help="For display in draft state"
    )
    note = fields.Text(
        string='Notes',
        size=1000,
    )

    @api.multi
    @api.depends('employee_id')
    def _compute_supervisor_emp_id(self):
        BossLevel = self.env['wkf.cmd.boss.level.approval']
        for rec in self:
            rec.supervisor_emp_id = \
                BossLevel.get_supervisor(rec.employee_id.id)

    @api.one
    @api.constrains('location_id', 'location_dest_id')
    def _check_location(self):
        if self.location_dest_id == self.location_id:
            raise ValidationError(_('Source and Destination Location '
                                    'can not be the same location'))

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        res = super(StockRequest, self).\
            fields_view_get(view_id=view_id, view_type=view_type,
                            toolbar=toolbar, submenu=submenu)
        if self._context.get('default_type') == 'request':
            res['arch'] = res['arch'].replace(
                'visible="draft,done"',
                'visible="draft,wait_confirm,confirmed,wait_approve,'
                'approved,ready,done"')
        if self._context.get('default_type') == 'transfer':
            res['arch'] = res['arch'].replace(
                'visible="draft,done"',
                'visible="draft,ready,done"')
        if self._context.get('default_type') == 'borrow':
            res['arch'] = res['arch'].replace(
                'visible="draft,done"',
                'visible="draft,wait_confirm,confirmed,wait_approve,'
                'approved,ready,done,done_return"')
            # For type = borrow, change name Transferred -> Waiting Return
            if 'state' in res['fields']:
                new_selection = []
                for s_tuple in res['fields']['state']['selection']:
                    s_list = list(s_tuple)
                    if s_list[0] == 'done':
                        s_list[1] = _('Waiting Return')
                    new_selection.append(tuple(s_list))
                res['fields']['state']['selection'] = new_selection
        return res

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('stock.transfer') or '/'
        return super(StockRequest, self).create(vals)

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        self.location_id = self.picking_type_id.default_location_src_id
        self.location_dest_id = self.picking_type_id.default_location_dest_id

    @api.model
    def _check_user_from_borrow_location(self):
        if self._context.get('default_type') == 'borrow':
            # Only user from the borrow location can prepare
            user_ou_ids = [g.id for g in self.env.user.operating_unit_ids]
            origin_ou_id = self.location_borrow_view_id.operating_unit_id.id
            if not (self.env.user.access_all_operating_unit or
                    origin_ou_id in user_ou_ids):
                raise ValidationError(_('Only user from the borrow location '
                                        'can process this request'))

    # Internal Actions
    @api.multi
    def action_request(self):
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError(_('No lines!'))
        self.write({'state': 'wait_confirm'})

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        # For case stock request, check confirm by supervisor in L only.
        if self.type == 'request' and self.supervisor_emp_id and \
                self._uid != self.supervisor_emp_id.user_id.id:
            raise ValidationError(
                _('You must be direct supervisor of %s %s to "Confirm".') %
                (self.employee_id.first_name, self.employee_id.last_name))
        # --
        if not self.line_ids:
            raise ValidationError(_('No lines!'))
        # self.line_ids._check_future_qty()
        self.write({'state': 'confirmed'})

    @api.multi
    def action_verify(self):
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError(_('No lines!'))
        self._check_user_from_borrow_location()
        self.line_ids._check_future_qty()
        self.write({'state': 'wait_approve'})

    @api.multi
    def action_approve(self):
        self.ensure_one()
        self._check_user_from_borrow_location()
        self.line_ids._check_future_qty()
        self.write({'state': 'approved'})

    @api.multi
    def action_prepare(self):
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError(_('No lines!'))
        if not self.receive_emp_id:
            raise ValidationError(_('Please select receiver!'))
        self._check_user_from_borrow_location()
        self.sudo().create_picking('transfer')  # Create
        self.transfer_picking_id.sudo().action_confirm()  # Confirm and reserve
        self.transfer_picking_id.sudo().action_assign()
        if self.sudo().transfer_picking_id.state != 'assigned':
            raise ValidationError(
                _('Requested material(s) not fully available!'))
        self.write({'state': 'ready'})

    @api.multi
    def action_transfer(self):
        self.ensure_one()
        if self._uid != self.receive_emp_id.user_id.id:
            raise ValidationError(
                _('You must be receiver to click "Transfer".'))
        if self.transfer_picking_id:
            self.transfer_picking_id.sudo().action_done()
        self.write({'state': 'done'})
        if self.type == 'borrow':  # prepare for return
            self.sudo().create_picking('return')

    @api.multi
    def action_return(self):
        self.ensure_one()
        self._check_user_from_borrow_location()
        if self.return_picking_id:
            self.return_picking_id.sudo().action_confirm()
            self.return_picking_id.sudo().action_assign()
            if self.sudo().return_picking_id.state != 'assigned':
                raise ValidationError(
                    _('Requested material(s) not fully available!'))
            self.return_picking_id.sudo().action_done()
        self.write({'state': 'done_return'})

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
            'date_done': fields.Datetime.now(),
            'picking_type_id': request.picking_type_id.id,
            'company_id': request.company_id.id,
            'move_type': 'direct',
            'note': request.note or "",
            'invoice_state': 'none',
        }
        return data

    @api.model
    def _prepare_picking_line(self, line, picking,
                              location_id,
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
            'location_id': location_id,
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
        if all(t == 'service' for t in
               self.line_ids.mapped('product_id.type')):
            raise ValidationError(
                _('Requested material(s) not of type stockable!'))
        picking = picking_obj.create(self._prepare_picking(self))
        location_id = False
        location_dest_id = False
        if ttype == 'transfer':
            self.write({'transfer_picking_id': picking.id})
            if self.type == 'borrow':
                location_id = self.location_borrow_id.id
                location_dest_id = self.location_id.id
            else:
                location_id = self.location_id.id
                location_dest_id = self.location_dest_id.id
        elif ttype == 'return':
            self.write({'return_picking_id': picking.id})
            if self.type == 'borrow':
                location_dest_id = self.location_borrow_id.id
                location_id = self.location_id.id
            else:
                location_dest_id = self.location_id.id
                location_id = self.location_dest_id.id
        for line in self.line_ids:
            if line.product_id and line.product_id.type == 'service':
                continue
            move_obj.sudo().create(
                self._prepare_picking_line(line, picking,
                                           location_id, location_dest_id))
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
        string='Verified Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        required=True,
    )
    product_uom = fields.Many2one(
        'product.uom',
        string='Unit of Measure',
        required=True,
    )
    product_uom_readonly = fields.Many2one(
        'product.uom',
        string='Unit of Measure',
        related='product_uom',
        readonly=True,
    )
    location_id = fields.Many2one(
        'stock.location',
        compute='_compute_location_id',
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
    state = fields.Selection(
        _STATES,
        related='request_id.state',
        string='Status',
        store=True,
    )

    @api.model
    def _get_location_id_by_type(self, ttype, location_id, location_borrow_id):
        return ttype == 'borrow' and location_borrow_id or location_id

    @api.multi
    def _compute_location_id(self):
        for rec in self:
            ttype = rec.sudo().request_id.type
            location_borrow_id = rec.sudo().request_id.location_borrow_id.id
            location_id = rec.sudo().request_id.location_id.id
            rec.location_id = self._get_location_id_by_type(ttype, location_id,
                                                            location_borrow_id)

    @api.multi
    def _set_product_qty(self, location_id):
        self.ensure_one()
        if self.product_id:
            UOM = self.env['product.uom']
            ctx = {'location': location_id}
            qty = self.product_id.with_context(ctx).sudo()._product_available()
            onhand_qty = qty[self.product_id.id]['qty_available']
            future_qty = qty[self.product_id.id]['virtual_available']
            self.onhand_qty = \
                UOM._compute_qty(self.product_id.uom_id.id,
                                 onhand_qty,
                                 self.product_uom.id)
            self.future_qty = \
                UOM._compute_qty(self.product_id.uom_id.id,
                                 future_qty,
                                 self.product_uom.id)

    @api.multi
    def _compute_product_available(self):
        for rec in self:
            location_id = rec.sudo().location_id.id
            rec._set_product_qty(location_id)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        request_type = self._context.get('request_type')
        location_borrow_id = self._context.get('location_borrow_id')
        request_location_id = self._context.get('location_id')
        location_id = self._get_location_id_by_type(request_type,
                                                    request_location_id,
                                                    location_borrow_id)
        self.product_uom = self.product_id.uom_id
        self._set_product_qty(location_id)

    @api.onchange('request_uom_qty')
    def _onchange_request_uom_qty(self):
        self.product_uom_qty = self.request_uom_qty

    @api.multi
    def _check_future_qty(self):
        for line in self:
            if line.product_uom_qty > line.future_qty:
                raise ValidationError(
                    _('%s is not enough!') % line.product_id.name)
