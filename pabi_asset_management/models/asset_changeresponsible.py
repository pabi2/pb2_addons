# -*- coding: utf-8 -*-
import logging
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class AccountAssetChangeresponsible(models.Model):
    _name = 'account.asset.changeresponsible'
    _inherit = ['mail.thread']
    _description = 'Asset Change Responsible'
    _order = 'name desc'
    
    name = fields.Char(
        string='Name',
        default='/',
        required=True,
        readonly=True,
        copy=False,
        size=500,
    )
    date = fields.Date(
        string='Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
        copy=False,
        readonly=False,
    )
    note = fields.Text(
        string='Note',
        copy=False,
        size=1000,
    )
    changeresponsible_ids = fields.One2many(
        'account.asset.changeresponsible.line',
        'changeresponsible_id',
        string='Changeresponsible Line',
        readonly=True,
        copy=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
        ('wait_confirm', 'Waiting for Confirmation'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('ready_transfer', 'Ready to Transfer'),
        ('done', 'Transferred'),
        ('cancel', 'Rejected')],
        string='Status',
        default='draft',
        readonly=True,
        copy=False,
        track_visibility='onchange',
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        default=lambda self: self.env['res.users'].
        operating_unit_default_get(self._uid),
        required=True,
    )
    requester_user_id = fields.Many2one(
        'res.users',
        string='Requester',
        default=lambda self: self.env.user,
        required=True,
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    supervisor_req_id = fields.Many2one(
        'hr.employee',
        string="Requester's Supervisor",
        store=True,
        readonly=True,
    )
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible Person',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    supervisor_res_id = fields.Many2one(
        'hr.employee',
        string="Responsible Supervisor",
        store=True,
        readonly=True,
    )
    search_ids = fields.Char(
        compute='_compute_search_ids',
        search='search_ids_search'
    )
    
    @api.one
    @api.depends('requester_user_id')
    def _compute_search_ids(self):
        print('View My Owner Change Master')

    def search_ids_search(self, operator, operand):
        procurement_user = self.env['pabi.security.line'].sudo().\
        search([('user_id','=',self.env.user.id),'|',('mg2','=',True),('mg3','=',True)])
        requester = self.search([('requester_user_id','=',self.env.user.id)]).ids
        requester_supervisor = self.search([('supervisor_req_id','=',self.env.user.id)]).ids
        responsible_person = self.search([('responsible_user_id','=',self.env.user.id)]).ids
        responsible_supervisor = self.search([('supervisor_res_id','=',self.env.user.id)]).ids
        asset_id = list(set().union(requester,requester_supervisor,responsible_person,responsible_supervisor))
        if procurement_user:
            org_id = self.env.user.partner_id.employee_id.org_id.id
            additional_org_id = self.env.user.partner_id.employee_id.org_ids.ids
            procurement_change = self.search(['|',('operating_unit_id.org_id','=',org_id)\
                                ,('operating_unit_id.org_id','in',additional_org_id)]).ids
            obj = list(set().union(asset_id,procurement_change))
            return [('id','in',obj)]
        else :
            return [('id','in',asset_id)]
    
    @api.multi
    @api.constrains('requester_user_id')
    @api.onchange('requester_user_id')
    def _onchange_supervisor_req_id(self):
        if self.requester_user_id:
            boss = self.requester_user_id.employee_id.id
            BossLevel = self.env['wkf.cmd.boss.level.approval']
            self.supervisor_req_id = BossLevel.get_supervisor(boss)
    
    @api.multi
    @api.constrains('responsible_user_id')
    @api.onchange('responsible_user_id')
    def _onchange_supervisor_res_id(self):
        if self.responsible_user_id:
            boss = self.responsible_user_id.employee_id.id
            BossLevel = self.env['wkf.cmd.boss.level.approval']
            self.supervisor_res_id = BossLevel.get_supervisor(boss)
            
    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
        
    @api.multi
    def action_wait_confirm(self):
        self.write({'state': 'wait_confirm'})   
    
    @api.multi
    def action_confirmed(self):
        for rec in self:
            if self.env.user.partner_id.employee_id != rec.supervisor_req_id:
                raise ValidationError(
                    _('Only %s can confirm this document!') %
                    (rec.supervisor_req_id.name))
        self.write({'state': 'confirmed'})
        
    @api.multi
    def action_approved(self):
        for rec in self:
            if self.env.user.partner_id.employee_id != rec.supervisor_res_id:
                raise ValidationError(
                    _('Only %s can approve this document!') %
                    (rec.supervisor_res_id.name))
        self.write({'state': 'approved'})     
        
    @api.multi
    def action_ready_transfer(self):
        for rec in self:
            if self.env.user != rec.responsible_user_id:
                raise ValidationError(
                    _('Only %s can receive this document!') %
                    (rec.responsible_user_id.name))
        self.write({'state': 'ready_transfer'})
    
    @api.multi
    def action_done(self):
        for rec in self:
            rec._validate_procurement_user()
            rec._changeresponsible()
        self.write({'state': 'done'})
        return True

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})
    
    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].\
                get('account.asset.changeresponsible') or '/'
        return super(AccountAssetChangeresponsible, self).create(vals)
    
    @api.multi
    def _validate_procurement_user(self):
        user_id = self.env.user.id
        procurement_user = self.env['pabi.security.line'].sudo().\
        search([('user_id','=',user_id),'|',('mg2','=',True),('mg3','=',True)])
        if procurement_user:
            return True
        else:
            raise ValidationError(_('Only Procurement User can approve this document!'))
    
    @api.multi
    def _changeresponsible(self):
        i = 0
        for line in self.changeresponsible_ids:
            i += 1
            _logger.info("Change Responsible %s/%s Running!!" % (i, len(self.changeresponsible_ids)))
            asset = line.asset_id
            new_master = {}
            #Info update
            if line.name:
                new_master['name'] = line.name
            if line.asset_brand:
                new_master['asset_brand'] = line.asset_brand
            if line.asset_model:
                new_master['asset_model'] = line.asset_model
            if line.serial_number:
                new_master['serial_number'] = line.serial_number
            if line.warranty_start_date:
                new_master['warranty_start_date'] = line.warranty_start_date
            if line.warranty_expire_date:
                new_master['warranty_expire_date'] = line.warranty_expire_date
            if line.note:
                new_master['note'] = line.note
            if line.building_id:
                new_master['building_id'] = line.building_id.id
            if line.floor_id:
                new_master['floor_id'] = line.floor_id.id
            if line.room_id:
                new_master['room_id'] = line.room_id.id
            new_master['responsible_user_id'] = self.responsible_user_id.id
            asset.write(new_master)
            _logger.info("Change Responsible %s/%s PASS!!" % (i, len(self.changeresponsible_ids)))
        return True

class AccountAssetChangeresponsibleLine(models.Model):
    _name = 'account.asset.changeresponsible.line'

    changeresponsible_id = fields.Many2one(
        'account.asset.changeresponsible',
        string='Asset User Changeresponsible',
        index=True,
        ondelete='cascade',
    )
    asset_id = fields.Many2one(
        'account.asset',
        string='Asset',
        required=True,
        ondelete='restrict',
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
    name = fields.Char(
        string='Name',
    )
    asset_brand = fields.Char(
        string='Brand',
    )
    asset_model = fields.Char(
        string='Model',
    )
    serial_number = fields.Char(
        string='Serial Number',
    )
    warranty_start_date = fields.Date(
        string='Warranty Start Date',
    )
    warranty_expire_date = fields.Date(
        string='Warranty Expire Date',
    )
    note = fields.Text(
        string='Notes',
    )
    # Target Owner
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
    )
    invest_asset_id = fields.Many2one(
        'res.invest.asset',
        string='Invest Asset',
    )
    invest_construction_phase_id = fields.Many2one(
        'res.invest.construction.phase',
        string='Construction Phase',
    )
    
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
        
    @api.multi
    @api.constrains('asset_id')
    @api.onchange('asset_id')
    def _onchange_depreciation_on(self):
        if self.asset_id:
            section = self.asset_id.owner_section_id
            self.section_id = section
            project = self.asset_id.owner_project_id
            self.project_id = project
            invest_asset = self.asset_id.owner_invest_asset_id
            self.invest_asset_id = invest_asset
            invest_construction = self.asset_id.owner_invest_construction_phase_id
            self.invest_construction_phase_id = invest_construction
