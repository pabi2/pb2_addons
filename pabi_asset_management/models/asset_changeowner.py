# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountAssetChangeowner(models.Model):
    _name = 'account.asset.changeowner'
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
        states={'draft': [('readonly', False)]},
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
    )
    # To New Owner
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
        compute='_compute_costcenter_id',
    )
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible By',
        required=True,
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    asset_ids = fields.Many2many(
        'account.asset.asset',
        'account_asset_asset_changeowner_rel',
        'changeowner_id', 'asset_id',
        string='Assets to Change Owner',
        domain=[('type', '!=', 'view')],
        copy=False,
        readonly=True,
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
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.asset_name = self.product_id.name

    @api.onchange('section_id')
    def _onchange_section_id(self):
        if self.section_id:
            self.project_id = False

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            self.section_id = False

    @api.multi
    @api.depends('project_id', 'section_id')
    def _compute_costcenter_id(self):
        for rec in self:
            if rec.project_id or rec. section_id:
                rec.costcenter_id = rec.project_id.costcenter_id or \
                    rec.section_id.costcenter_id

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
        Asset = self.env['account.asset.asset']
        Period = self.env['account.period']
        period = Period.find()
        # New Owner
        project = self.project_id
        section = self.section_id
        responsible_user = self.responsible_user_id.id
        # For change owner, no owner should be the same
        for asset in self.asset_ids:
            if (asset.project_id and asset.project_id == project) or \
                    (asset.section_id and asset.section_id == section):
                raise ValidationError(
                    _('Asset %s change to the same owner!') % (asset.code))
        new_owner = {'owner_project_id': project.id,
                     'owner_section_id': section.id,
                     'responsible_user': responsible_user.id, }
        # Moving of each asset to the new owner
        for asset in self.asset_ids:
            move_lines = []
            asset_move_lines_dict, depre_move_lines_dict = \
                Asset._prepare_asset_reverse_moves(asset)
            move_lines += asset_move_lines_dict + depre_move_lines_dict
            # Create move line for target asset
            # Asset
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
            move_dict = {'journal_id': asset.category_id.journal_id.id,
                         'line_id': final_move_lines,
                         'period_id': period.id,
                         'date': fields.Date.context_today(self),
                         'ref': self.name}
            AccountMove.with_context(allow_asset=True).create(move_dict)
            # Write back new owner
            asset.write(new_owner)
