# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountAssetRequest(models.Model):
    _name = 'account.asset.request'
    _inherit = ['mail.thread']
    _description = 'Asset Request'
    _order = 'name desc'

    name = fields.Char(
        string='Name',
        default='/',
        required=True,
        readonly=True,
        copy=False,
        size=500,
    )
    date_request = fields.Date(
        string='Request Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    user_id = fields.Many2one(
        'res.users',
        string='Preparer',
        default=lambda self: self.env.user,
        required=True,
        copy=False,
        readonly=True,
    )
    org_id = fields.Many2one(
        'res.org',
        related='user_id.partner_id.employee_id.org_id',
        string='Org',
        store=True,
        readonly=True,
    )
    approve_user_id = fields.Many2one(
        'res.users',
        string='Approver',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Preparer must select the approver for this task."
    )
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible Person',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Default purchase request user, but can change."
    )
    supervisor_res_id = fields.Many2one(
        'hr.employee', 
        string="Requester's Supervisor",
        #compute='_compute_supervisor_res_id',
        store=True,
        readonly=True,
    )    
    request_asset_ids = fields.One2many(
        'account.asset.request.line',
        'request_id',
        string='Assets to Move',
        readonly=True,
        copy=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Waiting Approval'),
         ('approve', 'Approved'),
         ('verify', 'Verify'),
         ('ready', 'Ready to Request'),
         ('done', 'Requested'),
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
        readonly=True,
        copy=False,
        track_visibility='onchange',
    )
    # Default
    building_id = fields.Many2one(
        'res.building',
        string='Building',
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
    )
    floor_id = fields.Many2one(
        'res.floor',
        string='Floor',
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
    )
    room_id = fields.Many2one(
        'res.room',
        string='Room',
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
    )

    @api.multi
    @api.constrains('responsible_user_id')
    @api.onchange('responsible_user_id')
    def _onchange_supervisor_res_id(self):
        if self.responsible_user_id:
            boss = self.responsible_user_id.employee_id.id
            BossLevel = self.env['wkf.cmd.boss.level.approval']
            self.supervisor_res_id = BossLevel.get_supervisor(boss)        
              
    # Building / Floor / Room
    @api.multi
    @api.constrains('building_id', 'floor_id', 'room_id')
    def _check_building(self):
        for rec in self:
            self.env['res.building']._check_room_location(rec.building_id,
                                                          rec.floor_id,
                                                          rec.room_id)

    @api.onchange('building_id')
    def _onchange_building_id(self):
        self.floor_id = False
        self.room_id = False

    @api.onchange('floor_id')
    def _onchange_floor_id(self):
        self.room_id = False

    @api.model
    def default_get(self, field_list):
        res = super(AccountAssetRequest, self).default_get(field_list)
        asset_ids = self._context.get('selected_asset_ids', [])
        building_id = self._context.get('default_building_id', False)
        floor_id = self._context.get('default_floor_id', False)
        room_id = self._context.get('default_room_id', False)
        responsible_user_id = \
            self._context.get('default_responsible_user_id', False)
        asset_request_lines = []
        for asset_id in asset_ids:
            asset_request_lines.append({
                'asset_id': asset_id,
                'building_id': building_id,
                'floor_id': floor_id,
                'room_id': room_id,
                'responsible_user_id': responsible_user_id})
        res['request_asset_ids'] = asset_request_lines
        return res

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            Fiscal = self.env['account.fiscalyear']
            vals['name'] = self.env['ir.sequence'].\
                with_context(fiscalyear_id=Fiscal.find(vals.get('date'))).\
                get('account.asset.request') or '/'
        return super(AccountAssetRequest, self).create(vals)

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_confirm(self):
        for rec in self:
            assets = rec.request_asset_ids.mapped('asset_id')
            assets.validate_asset_to_request()
        self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        for rec in self:
            assets = rec.request_asset_ids.mapped('asset_id')
            assets.validate_asset_to_request()
            if self.env.user != rec.approve_user_id:
                raise ValidationError(
                    _('Only %s can approve this document!') %
                    (rec.approve_user_id.name,))
        self.write({'state': 'approve'})
        
    @api.multi
    def action_verify(self):
        for rec in self:
            assets = rec.request_asset_ids.mapped('asset_id')
            assets.validate_asset_to_request()
            if self.env.user != rec.approve_user_id:
                raise ValidationError(
                    _('Only %s can approve this document!') %
                    (rec.approve_user_id.name,))
        self.write({'state': 'verify'})
      
    @api.multi    
    def action_ready(self):
        for rec in self:
            assets = rec.request_asset_ids.mapped('asset_id')
            assets.validate_asset_to_request()
            if self.env.user.partner_id.employee_id != rec.supervisor_res_id:
                raise ValidationError(
                    _('Only %s can approve this document!') %
                    (rec.supervisor_res_id.name))
        self.write({'state': 'ready'}) 
     
        
    @api.multi
    def action_done(self):
        for rec in self:
            assets = rec.request_asset_ids.mapped('asset_id')
            assets.validate_asset_to_request()
            if self.env.user != rec.responsible_user_id:
                raise ValidationError(
                    _('Only %s can request this document!') %
                    (rec.responsible_user_id.name,))
            for line in rec.request_asset_ids:
                line.asset_id.write({
                    'doc_request_id': rec.id,
                    'date_request': rec.date_request,
                    'responsible_user_id': rec.responsible_user_id.id,
                    'building_id': line.building_id.id,
                    'floor_id': line.floor_id.id,
                    'room_id': line.room_id.id,
                })
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        for rec in self:
            for line in rec.request_asset_ids:
                line.asset_id.write({
                    'doc_request_id': False,
                    'date_request': False,
                    'responsible_user_id': False,
                    'building_id': False,
                    'floor_id': False,
                    'room': False,
                })
        self.write({'state': 'cancel'})


class AccountAssetRequestLine(models.Model):
    _name = 'account.asset.request.line'

    request_id = fields.Many2one(
        'account.asset.request',
        string='Asset Request',
        ondelete='cascade',
        index=True,
        readonly=True,
    )
    asset_id = fields.Many2one(
        'account.asset',
        string='Asset',
        domain=[('doc_request_id', '=', False),
                ('type', '=', 'normal'),
                ('state', '=', 'open')],
        required=True,
        ondelete='restrict',
    )
    purchase_value = fields.Float(
        string='Purchase Value',
        related='asset_id.purchase_value',
        readonly=True,
    )
    building_id = fields.Many2one(
        'res.building',
        string='Building',
        ondelete='restrict',
    )
    floor_id = fields.Many2one(
        'res.floor',
        string='Floor',
        ondelete='restrict',
    )
    room_id = fields.Many2one(
        'res.room',
        string='Room',
        ondelete='restrict',
    )
    _sql_constraints = [
        ('asset_id_unique',
         'unique(asset_id, request_id)',
         'Duplicate assets selected!')
    ]

    # Building / Floor / Room
    @api.multi
    @api.constrains('building_id', 'floor_id', 'room_id')
    def _check_building(self):
        for rec in self:
            self.env['res.building']._check_room_location(rec.building_id,
                                                          rec.floor_id,
                                                          rec.room_id)

    # @api.onchange('building_id')
    # def _onchange_building_id(self):
    #     print self._context
    #     self.floor_id = False
    #     self.room_id = False
    #
    # @api.onchange('floor_id')
    # def _onchange_floor_id(self):
    #     self.room_id = False
