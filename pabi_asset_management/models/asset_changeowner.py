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
    
class AccountAssetChangeowner(models.Model):
    _name = 'account.asset.changeowner'
    _inherit = ['mail.thread']
    _description = 'Asset Change Owner'
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
    org_id = fields.Many2one(
        'res.org',
        related='user_id.partner_id.employee_id.org_id',
        string='Org',
        store=True,
        readonly=True,
    )
    note = fields.Text(
        string='Note',
        copy=False,
        size=1000,
    )
    changeowner_ids = fields.One2many(
        'account.asset.changeowner.line',
        'changeowner_id',
        string='Changeowner Line',
        readonly=True,
        copy=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Owner Changed'),
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
        readonly=True,
        copy=False,
        track_visibility='onchange',
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        domain=[('asset', '=', True), ('analytic_journal_id', '=', False)],
        readonly=True,
        required=True,
        help="Asset Journal (No-Budget)",
    )
    move_ids = fields.Many2many(
        'account.move',
        string='Journal Entries',
        compute='_compute_moves',
    )
    move_count = fields.Integer(
        string='JE Count',
        compute='_compute_moves',
    )
    
    changeowner_job_id = fields.Many2one(
        'queue.job',
        string='ChangeOwner Job',
        compute='_compute_changeowner_job_uuid',
    )
    changeowner_uuid = fields.Char(
        string='ChangeOwner Job UUID',
        compute='_compute_changeowner_job_uuid',
    )
    
    @api.multi
    def _compute_changeowner_job_uuid(self):
        for rec in self:
            task_name = "%s('%s', %s)" % \
                ('action_done_async_process', self._name, rec.id)
            jobs = self.env['queue.job'].search([
                ('func_string', 'like', task_name),
                ('state', '!=', 'done')],
                order='id desc', limit=1)
            rec.changeowner_job_id = jobs and jobs[0] or False
            rec.changeowner_uuid = jobs and jobs[0].uuid or False
        return True

    @api.multi
    def _compute_moves(self):
        for rec in self:
            rec.move_ids = rec.changeowner_ids.mapped('move_id')
            rec.move_count = len(rec.move_ids)
        return True

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].\
                get('account.asset.changeowner') or '/'
        return super(AccountAssetChangeowner, self).create(vals)

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_done(self):
        _logger.info("Change owner Starting!!")
        for rec in self:
            rec._changeowner()
        self.write({'state': 'done'})
        _logger.info("Change owner Completed!!")
        return True

    @api.multi
    def action_done_backgruond(self):
        if self._context.get('changeowner_async_process', False):
            self.ensure_one()
            if self._context.get('job_uuid', False):  # Called from @job
                return self.action_done()
            if self.changeowner_job_id:
                message = _('Confirm Change Owner')
                action = self.env.ref('pabi_utils.action_my_queue_job')
                raise RedirectWarning(message, action.id, _('Go to My Jobs'))
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = '%s - Confirm Change Owner' % self.name
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
    def _changeowner(self):
        """ The Concept
        * No new asset is being created
        * Update new owner (project, section) and run move lines
        * Source and target owner musfperiodt be different, otherwise, warning.
        Accoun Moves
        ============
        Dr Accumulated depreciation of transferring asset (if any)
            Cr Asset Value of trasferring asset
        Dr Asset Value to the new owner
            Cr Accumulated Depreciation of to the new owner (if any)
        """
        self.ensure_one()
        AccountMove = self.env['account.move']
        Period = self.env['account.period']
        i = 0
        for line in self.changeowner_ids:
            i += 1
            _logger.info("Change owner %s/%s Running!!" % (i, len(self.changeowner_ids)))
            if line.move_id:
                continue
            to_project = line.project_id
            to_section = line.section_id
            to_invest_asset = line.invest_asset_id
            to_invest_construction_phase = line.invest_construction_phase_id
            # At lease 1 dimension should be selected
            budgets = (to_project.id, to_section.id,
                       to_invest_asset.id, to_invest_construction_phase.id)
            if len(filter(lambda x: x, budgets)) == 0:
                raise ValidationError(_('No new owner selected!'))
            # For change owner, no owner should be the same
            asset = line.asset_id
            if (asset.owner_project_id == to_project) and \
                    (asset.owner_section_id == to_section) and \
                    (asset.invest_asset_id == to_invest_asset) and \
                    (asset.invest_construction_phase_id ==
                     to_invest_construction_phase):
                raise ValidationError(
                    _('Asset %s changes to the same owner!') % (asset.code))
            new_owner = {'owner_project_id': to_project.id,
                         'owner_section_id': to_section.id,
                         'owner_invest_asset_id': to_invest_asset.id,
                         'owner_invest_construction_phase_id':
                         to_invest_construction_phase.id}
            # Moving to new owner Project/Section
            move_lines = []
            if asset.purchase_value:
                move_lines += [
                    # Cr Asset Value (Old)
                    {
                        'asset_id': asset.id,
                        'account_id': asset.profile_id.account_asset_id.id,
                        'partner_id': asset.partner_id.id,
                        'name': asset.display_name,
                        # Value
                        'credit': (asset.purchase_value > 0.0 and
                                   asset.purchase_value or 0.0),
                        'debit': (asset.purchase_value < 0.0 and
                                  -asset.purchase_value or 0.0),
                        # Budget
                        'project_id': asset.owner_project_id.id,
                        'section_id': asset.owner_section_id.id,
                        'invest_asset_id': asset.owner_invest_asset_id.id,
                        'invest_construction_phase_id':
                        asset.owner_invest_construction_phase_id.id,
                     },
                    # Dr Asset Value (New)
                    {
                        'asset_id': asset.id,
                        'account_id': asset.profile_id.account_asset_id.id,
                        'partner_id': asset.partner_id.id,
                        'name': asset.display_name,
                        # Value
                        'credit': (asset.purchase_value < 0.0 and
                                   -asset.purchase_value or 0.0),
                        'debit': (asset.purchase_value > 0.0 and
                                  asset.purchase_value or 0.0),
                        # Budget
                        'project_id': to_project.id,
                        'section_id': to_section.id,
                        'invest_asset_id': to_invest_asset.id,
                        'invest_construction_phase_id':
                        to_invest_construction_phase.id,
                     },
                ]
            if asset.value_depreciated:
                move_lines += [
                    # Dr Accum Depre (Old)
                    {
                        'asset_id': asset.id,
                        'account_id':
                        asset.profile_id.account_depreciation_id.id,
                        'partner_id': asset.partner_id.id,
                        'name': asset.display_name,
                        # Value
                        'credit': (asset.value_depreciated < 0.0 and
                                   -asset.value_depreciated or 0.0),
                        'debit': (asset.value_depreciated > 0.0 and
                                  asset.value_depreciated or 0.0),
                        # Budget
                        'project_id': asset.owner_project_id.id,
                        'section_id': asset.owner_section_id.id,
                        'invest_asset_id': asset.owner_invest_asset_id.id,
                        'invest_construction_phase_id':
                        asset.owner_invest_construction_phase_id.id,
                     },
                    # Cr Accum Depre (New)
                    {
                        'asset_id': asset.id,
                        'account_id':
                        asset.profile_id.account_depreciation_id.id,
                        'partner_id': asset.partner_id.id,
                        'name': asset.display_name,
                        # Value
                        'credit': (asset.value_depreciated > 0.0 and
                                   asset.value_depreciated or 0.0),
                        'debit': (asset.value_depreciated < 0.0 and
                                  -asset.value_depreciated or 0.0),
                        # Budget
                        'project_id': to_project.id,
                        'section_id': to_section.id,
                        'invest_asset_id': to_invest_asset.id,
                        'invest_construction_phase_id':
                        to_invest_construction_phase.id,
                     },
                ]
            # Finalize all moves before create it.
            final_move_lines = [(0, 0, x) for x in move_lines]
            if final_move_lines:
                move_dict = {
                    # Force using AN
                    'journal_id': self.journal_id.id,
                    # 'journal_id': asset.profile_id.journal_id.id,
                    'line_id': final_move_lines,
                    'period_id': Period.find(self.date).id,
                    'date': self.date,
                    'ref': self.name}
                # direct_create = compute chartfield on post
                ctx = {'allow_asset': True, 'direct_create': True,
                       'no_test_chartfield_active': True}
                line.move_id = \
                    AccountMove.with_context(ctx).create(move_dict)
            # Asset Owner Info update
            if line.responsible_user_id:
                new_owner['responsible_user_id'] = line.responsible_user_id.id
            if line.building_id:
                new_owner['building_id'] = line.building_id.id
            if line.floor_id:
                new_owner['floor_id'] = line.floor_id.id
            if line.room_id:
                new_owner['room_id'] = line.room_id.id
            asset.write(new_owner)
            _logger.info("Change owner %s/%s PASS!!" % (i, len(self.changeowner_ids)))
        return True

    @api.multi
    @api.constrains('changeowner_ids')
    def _check_changeowner_ids(self):
        for rec in self:
            if len(rec.changeowner_ids) != \
                    len(rec.changeowner_ids.mapped('asset_id')):
                raise ValidationError(_('Duplicate asset in line!'))

    @api.multi
    def open_entries(self):
        self.ensure_one()
        return {
            'name': _("Journal Entries"),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': self._context,
            'nodestroy': True,
            'domain': [('id', 'in', self.move_ids.ids)],
        }


class AccountAssetChangeownerLine(models.Model):
    _name = 'account.asset.changeowner.line'

    changeowner_id = fields.Many2one(
        'account.asset.changeowner',
        string='Asset Changeowner',
        index=True,
        ondelete='cascade',
    )
    asset_id = fields.Many2one(
        'account.asset',
        string='Asset',
        domain=[('state', '=', 'open')],
        required=True,
        ondelete='restrict',
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        copy=False,
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

    @api.onchange('section_id')
    def _onchange_section_id(self):
        if self.section_id:
            self.project_id = False
            self.invest_asset_id = False
            self.invest_construction_phase_id = False

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            self.section_id = False
            self.invest_asset_id = False
            self.invest_construction_phase_id = False

    @api.onchange('invest_asset_id')
    def _onchange_invest_asset_id(self):
        if self.invest_asset_id:
            self.section_id = False
            self.project_id = False
            self.invest_construction_phase_id = False

    @api.onchange('invest_construction_phase_id')
    def _onchange_invest_construction_phase_id(self):
        if self.invest_construction_phase_id:
            self.section_id = False
            self.project_id = False
            self.invest_asset_id = False

    @api.multi
    @api.constrains('section_id', 'project_id', 'invest_asset_id',
                    'invest_construction_phase_id')
    def _check_budget_dimension(self):
        for rec in self:
            budgets = (rec.section_id.id,
                       rec.project_id.id,
                       rec.invest_asset_id.id,
                       rec.invest_construction_phase_id.id)
            if len(filter(lambda x: x, budgets)) > 1:
                raise ValidationError(
                    _('Please choose only one budget dimension!'))
