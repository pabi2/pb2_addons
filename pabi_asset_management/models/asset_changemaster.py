# -*- coding: utf-8 -*-
import logging
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.exceptions import RedirectWarning
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import RetryableJobError

_logger = logging.getLogger(__name__)

@job(default_channel='root.single_queue')
def action_done_async_process(session, model_name, res_id):
    try:
        res = session.pool[model_name].action_done_backgruond(
            session.cr, session.uid, [res_id], session.context)
        return {'result': res}
    except Exception, e:
        raise RetryableJobError(e)
    
class AccountAssetChangemaster(models.Model):
    _name = 'account.asset.changemaster'
    _inherit = ['mail.thread']
    _description = 'Asset Change Master'
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
        string='Prepared By',
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
        'account.asset.changemaster.line',
        'changemaster_id',
        string='Changemaster Line',
        readonly=True,
        copy=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Master Changed'),
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
        readonly=True,
        copy=False,
        track_visibility='onchange',
    )
    changemaster_job_id = fields.Many2one(
        'queue.job',
        string='ChangeMaster Job',
        compute='_compute_changemaster_job_uuid',
    )
    changemaster_uuid = fields.Char(
        string='ChangeMaster Job UUID',
        compute='_compute_changemaster_job_uuid',
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        default=lambda self: self.env['res.users'].
        operating_unit_default_get(self._uid),
        required=True,
    )

    
    @api.multi
    def _compute_changemaster_job_uuid(self):
        for rec in self:
            task_name = "%s('%s', %s)" % \
                ('action_done_async_process', self._name, rec.id)
            jobs = self.env['queue.job'].search([
                ('func_string', 'like', task_name),
                ('state', '!=', 'done')],
                order='id desc', limit=1)
            rec.changemaster_job_id = jobs and jobs[0] or False
            rec.changemaster_uuid = jobs and jobs[0].uuid or False
        return True

    @api.multi
    def _compute_moves(self):
        for rec in self:
            rec.move_ids = rec.changemaster_ids.mapped('move_id')
            rec.move_count = len(rec.move_ids)
        return True

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].\
                get('account.asset.changemaster') or '/'
        return super(AccountAssetChangemaster, self).create(vals)

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_done(self):
        for rec in self:
            rec._changemaster()
        self.write({'state': 'done'})
        return True

    @api.multi
    def action_done_backgruond(self):
        if self._context.get('changemaster_async_process', False):
            self.ensure_one()
            if self._context.get('job_uuid', False):  # Called from @job
                return self.action_done()
            if self.changemaster_job_id:
                message = _('Confirm Change Master')
                action = self.env.ref('pabi_utils.action_my_queue_job')
                raise RedirectWarning(message, action.id, _('Go to My Jobs'))
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = '%s - Confirm Change Master' % self.name
            uuid = action_done_async_process.delay(
                session, self._name, self.id, description=description)
            job = self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
            # Process Name
            #job.process_id = self.env.ref('pabi_async_process.'
            #                              'confirm_pos_order')
        else:
            return self.action_done()
    
    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def _changemaster(self):
        i = 0
        for line in self.changemaster_ids:
            i += 1
            _logger.info("Change master %s/%s Running!!" % (i, len(self.changemaster_ids)))
            to_name = line.name
            to_asset_brand = line.asset_brand
            to_asset_model = line.asset_model
            to_asset_purchase_method_id = line.asset_purchase_method_id
            to_responsible_user_id = line.responsible_user_id
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
                    (asset.asset_purchase_method_id == to_asset_purchase_method_id) and \
                    (asset.responsible_user_id == to_responsible_user_id) and \
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
            if line.responsible_user_id:
                new_master['responsible_user_id'] = line.responsible_user_id.id
            if line.building_id:
                new_master['building_id'] = line.building_id.id
            if line.floor_id:
                new_master['floor_id'] = line.floor_id.id
            if line.room_id:
                new_master['room_id'] = line.room_id.id
            if line.asset_purchase_method_id:
                new_master['asset_purchase_method_id'] = line.asset_purchase_method_id.id
            asset.write(new_master)
            _logger.info("Change master %s/%s PASS!!" % (i, len(self.changemaster_ids)))
        return True

    @api.multi
    @api.constrains('changemaster_ids')
    def _check_changemaster_ids(self):
        for rec in self:
            if len(rec.changemaster_ids) != \
                    len(rec.changemaster_ids.mapped('asset_id')):
                raise ValidationError(_('Duplicate asset in line!'))


class AccountAssetChangemasterLine(models.Model):
    _name = 'account.asset.changemaster.line'

    changemaster_id = fields.Many2one(
        'account.asset.changemaster',
        string='Asset Changemaster',
        index=True,
        ondelete='cascade',
    )
    asset_id = fields.Many2one(
        'account.asset',
        string='Asset',
        required=True,
        ondelete='restrict',
    )
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible By',
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
    asset_purchase_method_id = fields.Many2one(
        'asset.purchase.method',
        string='Purchase Method',
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
        
