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
         ('done', 'Requested'),
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
        readonly=True,
        copy=False,
        track_visibility='onchange',
    )
    # Default
    location_id = fields.Many2one(
        'account.asset.location',
        string='Default Building',
    )
    room = fields.Char(
        string='Default Room',
    )

    @api.model
    def default_get(self, field_list):
        res = super(AccountAssetRequest, self).default_get(field_list)
        asset_ids = self._context.get('selected_asset_ids', [])
        location_id = self._context.get('default_location_id', False)
        room = self._context.get('default_room', False)
        responsible_user_id = \
            self._context.get('default_responsible_user_id', False)
        asset_request_lines = []
        for asset_id in asset_ids:
            asset_request_lines.append({
                'asset_id': asset_id,
                'location_id': location_id,
                'room': room,
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
                    'location_id': line.location_id.id,
                    'room': line.room,
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
                    'location_id': False,
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
    location_id = fields.Many2one(
        'account.asset.location',
        string='Building',
        required=True,
    )
    room = fields.Char(
        string='Room',
        required=True,
    )
    _sql_constraints = [
        ('asset_id_unique',
         'unique(asset_id, request_id)',
         'Duplicate assets selected!')
    ]
