# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountAssetTransfer(models.Model):
    _name = 'account.asset.transfer'

    name = fields.Char(
        string='Name',
        default='/',
        required=True,
    )
    date = fields.Date(
        string='Date',
        default=lambda self: fields.Date.context_today(self),
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        rquired=True,
    )
    note = fields.Text(
        string='Note',
    )
    # To Asset Type
    product_id = fields.Many2one(
        'product.product',
        string='To Asset Type',
        domain=[('asset', '=', True)],
    )
    asset_category_id = fields.Many2one(
        'account.asset.category',
        related='product_id.asset_category_id',
        string='To Asset Category',
        store=True,
        readonly=True,
    )
    ref_asset_id = fields.Many2one(
        'account.asset.asset',
        string='Asset Created',
        readonly=True,
    )
    transfer_asset_ids = fields.Many2many(
        'account.asset.asset',
        'account_asset_asset_transfer_rel', 'transfer_id', 'asset_id',
        string='Assets to Transfer',
        domain=[('type', '!=', 'view'), ('no_depreciation', '=', True)],
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('transfer', 'Transferred'),
         ('cancel', 'Cancelled')],
        string='Status',
        state='draft',
        readonly=True,
    )

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_transfer(self):
        self.write({'state': 'transfer'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})
