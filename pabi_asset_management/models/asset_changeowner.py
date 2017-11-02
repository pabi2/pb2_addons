# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


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
    )
    date = fields.Date(
        string='Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
        copy=False,
        readonly=True,
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
        for rec in self:
            rec._changeowner()
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def _changeowner(self):
        """ The Concept
        * No new assect is being created
        * Update new owner (project, section) and run move lines
        * Source and target owner must be different, otherwise, warning.
        Accoun Moves
        ============
        Dr Accumulated depreciation of transferring asset (if any)
            Cr Asset Value of trasferring asset
        Dr Asset Value to the new owner
            Cr Accumulated Depreciation of to the new owner (if any)
        """
        self.ensure_one()
        AccountMove = self.env['account.move']
        Asset = self.env['account.asset']
        Period = self.env['account.period']
        period = Period.find()
        for line in self.changeowner_ids:
            project = line.project_id
            section = line.section_id
            # For change owner, no owner should be the same
            asset = line.asset_id
            if (project and asset.owner_project_id == project) or \
                    (section and asset.owner_section_id == section):
                raise ValidationError(
                    _('Asset %s changes to the same owner!') % (asset.code))
            new_owner = {'owner_project_id': project.id,
                         'owner_section_id': section.id}
            # Moving to new owner Project/Section
            if new_owner.get('owner_project_id') or \
                    new_owner.get('owner_section_id'):
                move_lines = []
                asset_move_lines_dict, depre_move_lines_dict = \
                    Asset._prepare_asset_reverse_moves(asset)
                move_lines += asset_move_lines_dict + depre_move_lines_dict
                # Create move line for target asset
                # Asset
                if asset_move_lines_dict:
                    new_asset_move_line_dict = \
                        Asset._prepare_asset_target_move(asset_move_lines_dict,
                                                         new_owner)
                    move_lines.append(new_asset_move_line_dict)
                # Depre
                if depre_move_lines_dict:
                    new_depre_move_lines_dict = \
                        Asset._prepare_asset_target_move(depre_move_lines_dict,
                                                         new_owner)
                    move_lines.append(new_depre_move_lines_dict)
                # Finalize all moves before create it.
                final_move_lines = [(0, 0, x) for x in move_lines]
                move_dict = {'journal_id': asset.profile_id.journal_id.id,
                             'line_id': final_move_lines,
                             'period_id': period.id,
                             'date': fields.Date.context_today(self),
                             'ref': self.name}
                AccountMove.with_context(allow_asset=True).create(move_dict)
            # Asset Owner Info update
            if line.responsible_user_id:
                new_owner['responsible_user_id'] = line.responsible_user_id.id
            if line.location_id:
                new_owner['location_id'] = line.location_id.id
            if line.room:
                new_owner['room'] = line.room
            asset.write(new_owner)

    @api.multi
    @api.constrains('changeowner_ids')
    def _check_changeowner_ids(self):
        for rec in self:
            if len(rec.changeowner_ids) != \
                    len(rec.changeowner_ids.mapped('asset_id')):
                raise ValidationError(_('Duplicate asset in line!'))


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
    # Target Owner
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
    )
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible By',
    )
    location_id = fields.Many2one(
        'account.asset.location',
        string='Building',
    )
    room = fields.Char(
        string='Room',
    )

    @api.onchange('section_id')
    def _onchange_section_id(self):
        if self.section_id:
            self.project_id = False

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            self.section_id = False

    @api.multi
    @api.constrains('section_id', 'project_id')
    def _check_section_project(self):
        for rec in self:
            if rec.section_id and rec.project_id:
                raise ValidationError(
                    _('Please choose only project or section!'))
