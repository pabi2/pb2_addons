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
    date = fields.Date(
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
    receive_user_id = fields.Many2one(
        'res.users',
        string='Responsible Person',
        required=True,
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Default purchase request user, but can change."
    )
    issue_asset_ids = fields.Many2many(
        'account.asset.asset',
        'account_asset_asset_issue_rel',
        'issue_id', 'asset_id',
        string='Assets to Issue',
        domain=[('issued', '=', False)],
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
            rec.issue_asset_ids.write({'issued': True})
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.issue_asset_ids.write({'issued': False})
        self.write({'state': 'cancel'})
