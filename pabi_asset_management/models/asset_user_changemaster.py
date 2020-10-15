# -*- coding: utf-8 -*-
import logging
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class AccountAssetUserChangemaster(models.Model):
    _name = 'account.asset.user.changemaster'
    _inherit = ['mail.thread']
    _description = 'Asset Change Master By User'
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
    user_id = fields.Many2one(
        'res.users',
        string='Requester',
        default=lambda self: self.env.user,
        required=True,
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    note = fields.Text(
        string='Note',
        copy=False,
        size=1000,
    )
    changemaster_ids = fields.One2many(
        'account.asset.user.changemaster.line',
        'changemaster_id',
        string='Changemaster Line',
        readonly=True,
        copy=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('wait', 'Waiting for Approved'),
         ('done', 'Approved'),
         ('cancel', 'Cancelled')],
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
    
    search_ids = fields.Char(
        compute='_compute_search_ids',
        search='search_ids_search'
    )
    
    @api.one
    @api.depends('user_id')
    def _compute_search_ids(self):
        print('View My Owner Change Master')

    def search_ids_search(self, operator, operand):
        procurement_user = self.env['pabi.security.line'].sudo().\
        search([('user_id','=',self.env.user.id),'|',('mg2','=',True),('mg3','=',True)])
        my_change = self.search([('user_id','=',self.env.user.id)]).ids
        if procurement_user:
            org_id = self.env.user.partner_id.employee_id.org_id.id
            additional_org_id = self.env.user.partner_id.employee_id.org_ids.ids
            procurement_change = self.search(['|',('operating_unit_id.org_id','=',org_id)\
                                ,('operating_unit_id.org_id','in',additional_org_id)]).ids
            obj = list(set().union(my_change,procurement_change))
            return [('id','in',obj)]
        else :
            return [('id','in',my_change)]
    
    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_wait(self):
        self.state = 'wait'

    @api.multi
    def action_done(self):
        for rec in self:
            rec._validate_procurement_user()
            rec._changemaster()
        self.state = 'done'
        
    @api.multi
    def action_cancel(self):
        self.state = 'cancel'
        
    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].\
                get('account.asset.user.changemaster') or '/'
        return super(AccountAssetUserChangemaster, self).create(vals)
    
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
    def _changemaster(self):
        i = 0
        for line in self.changemaster_ids:
            i += 1
            _logger.info("Change master %s/%s Running!!" % (i, len(self.changemaster_ids)))
            to_name = line.name
            to_asset_brand = line.asset_brand
            to_asset_model = line.asset_model
            to_building_id = line.building_id
            to_floor_id = line.floor_id
            to_room_id = line.room_id
            to_serial_number = line.serial_number
            to_warranty_start_date = line.warranty_start_date
            to_warranty_expire_date = line.warranty_expire_date
            to_note = line.note
            # For change master, no master should be the same
            asset = line.asset_id
            if (asset.name == to_name) and \
                    (asset.asset_brand == to_asset_brand) and \
                    (asset.asset_model == to_asset_model) and \
                    (asset.building_id == to_building_id) and \
                    (asset.floor_id == to_floor_id) and \
                    (asset.room_id == to_room_id) and \
                    (asset.serial_number == to_serial_number) and \
                    (asset.warranty_start_date == to_warranty_start_date) and \
                    (asset.warranty_expire_date == to_warranty_expire_date) and \
                    (asset.note == to_note):
                raise ValidationError(_('Asset %s changes to the same master!') % (asset.code))
            new_master = {}
            # Asset Master Info update
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
            asset.write(new_master)
            _logger.info("Change master %s/%s PASS!!" % (i, len(self.changemaster_ids)))
        return True
    
class AccountAssetUserChangemasterLine(models.Model):
    _name = 'account.asset.user.changemaster.line'

    changemaster_id = fields.Many2one(
        'account.asset.user.changemaster',
        string='Asset User Changemaster',
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