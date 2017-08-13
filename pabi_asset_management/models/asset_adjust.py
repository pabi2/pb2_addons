# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.tools import float_compare


class AccountAssetAdjust(models.Model):
    _name = 'account.asset.adjust'
    _inherit = ['mail.thread']
    _description = 'Asset Adjust'
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
        states={'draft2': [('readonly', False)]},
    )
    user_id = fields.Many2one(
        'res.users',
        string='Prepared By',
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
    note = fields.Text(
        string='Note',
        copy=False,
    )
    adjust_line_ids = fields.One2many(
        'account.asset.adjust.line',
        'adjust_id',
        string='Asset Adjustment',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    adjust_type = fields.Selection(
        [('asset_type', 'Change Asset Type')],
        string='Adjust Type',
        copy=True,
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Source Assets'),
         ('done', 'Adjustred'),
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
        readonly=True,
        copy=False,
        track_visibility='onchange',
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Ref Supplier Invoice',
        domain=[('type', '=', 'in_invoice'),
                ('state', 'in', ('open', 'paid'))],
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].\
                get('account.asset.adjust') or '/'
        return super(AccountAssetAdjust, self).create(vals)

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_done(self):
        for rec in self:
            # rec._validate_asset_values()
            if rec.adjust_type == 'asset_type':
                rec._adjust_asset_type()
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.onchange('adjust_type', 'invoice_id')
    def _onchange_adjust_type_invoice(self):
        self.adjust_line_ids = False
        if not (self.adjust_type == 'asset_type' and self.invoice_id):
            return
        invoice_asset_lines = self.invoice_id.\
            invoice_line.filtered(lambda l: l.product_id.asset)
        asset_moves = invoice_asset_lines.mapped('move_id')
        asset_picks = asset_moves.mapped('picking_id')
        Asset = self.env['account.asset']
        assets = Asset.search([('picking_id', 'in', asset_picks.ids)])
        # Check if this adjustment is created from Suplier Invoice action
        src_invoice_id = self._context.get('default_invoice_id', False)
        adjust_asset_type_dict = \
            self._context.get('adjust_asset_type_dict', {})
        for asset in assets:
            if src_invoice_id and \
                    str(asset.product_id.id) not in adjust_asset_type_dict:
                continue
            adjust_line = self.env['account.asset.adjust.line'].new()
            adjust_line.asset_id = asset
            # adjust_line.date_remove = fields.Date.context_today(self)
            # STD-REMOVE
            # adjust_line._onchange_asset_id()
            # --
            # New Asset
            adjust_line.product_id = \
                adjust_asset_type_dict[str(asset.product_id.id)]
            self.adjust_line_ids += adjust_line

    @api.multi
    def _adjust_asset_type(self):
        """ The Concept
        * Remove the origin asset (asset removal)
        * Create new type of asset (direct creation)
        * Create reference from new asset to the old one
        """
        self.ensure_one()
        if not self.adjust_line_ids:
            raise ValidationError(_('No asset to remove!'))
        if self.adjust_line_ids.filtered(lambda l: l.asset_id.state != 'open'):
            raise ValidationError(_('Only running asset can be adjusted!'))
        for line in self.adjust_line_ids:
            # Simple Removal (same as in asset removal)
            asset = line.asset_id
            ctx = {'active_ids': [asset.id], 'active_id': asset.id}
            if asset.value_residual:
                ctx.update({'early_removal': True})
            line.with_context(ctx).remove()
            asset.status = line.target_status
            # Simple duplicate to new asset type, name
            new_asset = asset.copy({
                'profile_id': line.asset_profile_id.id,
                'product_id': line.product_id.id,
                'name': line.asset_name,
            })
            line.write({'ref_asset_id': new_asset.id,
                        'active': False})

    @api.multi
    def _remove_adjusting_assets(self):
        self.ensure_one()
        if not self.adjust_line_ids:
            raise ValidationError(_('No asset to remove!'))
        if self.adjust_line_ids.filtered(lambda l: l.asset_id.state != 'open'):
            raise ValidationError(_('Only running asset can be adjusted!'))
        for line in self.adjust_line_ids:
            asset = line.asset_id
            ctx = {'active_ids': [asset.id], 'active_id': asset.id}
            if asset.value_residual:
                ctx.update({'early_removal': True})
            line.with_context(ctx).remove()
            asset.status = line.target_status


class AccountAssetAdjustLine(models.Model):
    _name = 'account.asset.adjust.line'
    # _inherit = 'account.asset.remove'

    adjust_id = fields.Many2one(
        'account.asset.adjust',
        string='Asset Adjust',
        index=True,
        ondelete='cascade',
    )
    asset_id = fields.Many2one(
        'account.asset',
        string='Origin Asset',
        domain=[('type', '!=', 'view'),
                ('profile_type', 'not in', ('ait', 'auc')),
                ('state', '=', 'open'),
                '|', ('active', '=', True), ('active', '=', False)],
        help="Asset to be removed, as it create new asset of the same value",
    )
    product_id = fields.Many2one(
        'product.product',
        string='To Asset Type',
        domain=[('asset', '=', True)],
        required=True,
    )
    asset_name = fields.Char(
        string='Asset Name',
        required=True,
        help="Default with original asset name, but can be chagned.",
    )
    asset_profile_id = fields.Many2one(
        'account.asset.profile',
        related='product_id.asset_profile_id',
        string='To Asset Profile',
        store=True,
        readonly=True,
    )
    ref_asset_id = fields.Many2one(
        'account.asset',
        string='New Asset',
        readonly=True,
    )
    target_status = fields.Many2one(
        'account.asset.status',
        string='Asset Status',
        domain="[('map_state', '=', 'removed')]",
        required=True,
    )
    _sql_constraints = [
        ('asset_id_unique',
         'unique(asset_id, adjust_id)',
         'Duplicate assets selected!')
    ]

    # STD-REMOVE
    # @api.onchange('asset_id')
    # def _onchange_asset_id(self):
    #     Remove = self.env['account.asset.remove'].\
    #         with_context(active_id=self.asset_id.id)
    #     if self.asset_id:
    #         vals = Remove._get_sale()
    #         self.sale_value = vals['sale_value']
    #         self.account_sale_id = vals['account_sale_id']
    #         self.account_plus_value_id = \
    #             Remove._default_account_plus_value_id()
    #         self.account_min_value_id = \
    #             Remove._default_account_min_value_id()
    #         self.account_residual_value_id = \
    #             Remove._default_account_residual_value_id()
    #         self.posting_regime = Remove._get_posting_regime()
    # --

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.asset_name = self.product_id.name
