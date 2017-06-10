# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountAssetIssue(models.Model):
    _name = 'account.asset.issue'
    _description = 'Printout asset issue form'
    _order = 'name desc'

    name = fields.Char(
        string='Name',
        default='/',
        required=True,
        readonly=True,
        copy=False,
    )
    date_issue = fields.Date(
        string='Issue Date',
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
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible Person',
        required=True,
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Default purchase request user, but can change."
    )
    issue_asset_ids = fields.One2many(
        'account.asset.issue.line',
        'issue_id',
        string='Assets to Issue',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Issued'),
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
                get('account.asset.issue') or '/'
        return super(AccountAssetIssue, self).create(vals)

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_done(self):
        for rec in self:
            for line in rec.issue_asset_ids:
                line.asset_id.write({
                    'doc_issue_id': rec.id,
                    'date_issue': rec.date_issue,
                    'responsible_user_id': rec.responsible_user_id.id,
                    'location_id': line.location_id.id,
                    'room': line.room,
                })
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        for rec in self:
            for line in rec.issue_asset_ids:
                line.asset_id.write({
                    'doc_issue_id': False,
                    'date_issue': False,
                    'responsible_user_id': False,
                    'location_id': False,
                    'room': False,
                })
        self.write({'state': 'cancel'})


class AccountAssetIssueLine(models.Model):
    _name = 'account.asset.issue.line'

    issue_id = fields.Many2one(
        'account.asset.issue',
        string='Asset Issue',
        ondelete='cascade',
        index=True,
        readonly=True,
    )
    asset_id = fields.Many2one(
        'account.asset.asset',
        string='Asset',
        domain=[('doc_issue_id', '=', False)],
        required=True,
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Building',
        required=True,
    )
    room = fields.Char(
        string='Room',
        required=True,
    )
    _sql_constraints = [
        ('asset_id_unique',
         'unique(asset_id, issue_id)',
         'Duplicate assets selected!')
    ]
