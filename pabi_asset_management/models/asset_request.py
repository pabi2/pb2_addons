# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountAssetRequest(models.Model):
    _name = 'account.asset.request'
    _description = 'Printout asset request form'
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
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Default purchase request user, but can change."
    )
    request_asset_ids = fields.One2many(
        'account.asset.request.line',
        'request_id',
        string='Assets to Move',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Waiting Approval'),
         ('done', 'Requested'),
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
        readonly=True,
        copy=False,
    )

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
        self.write({'state': 'confirm'})

    @api.multi
    def action_done(self):
        for rec in self:
            if self.env.user != rec.approve_user_id:
                raise ValidationError(
                    _('Only %s can approve this document!') %
                    (rec.approve_user_id.name,))
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
        'account.asset.asset',
        string='Asset',
        domain=[('doc_request_id', '=', False)],
        required=True,
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
