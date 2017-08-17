# -*- coding: utf-8 -*-
import ast
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
    adjust_type = fields.Selection(
        [('asset_type', 'Change Asset Type'),
         ('asset_to_expense', 'Asset => Expense'),
         ('expense_to_asset', 'Expense => Asset')],
        string='Adjust Type',
        copy=True,
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Adjusted'),
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
    adjust_line_ids = fields.One2many(
        'account.asset.adjust.line',
        'adjust_id',
        string='Asset Adjustment',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    adjust_asset_to_expense_ids = fields.One2many(
        'account.asset.adjust.asset_to_expense',
        'adjust_id',
        string='Asset to Expense Adjustment',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    adjust_expense_to_asset_ids = fields.One2many(
        'account.asset.adjust.expense_to_asset',
        'adjust_id',
        string='Expense to Asset Adjustment',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    old_asset_count = fields.Integer(
        string='Old Asset Count',
        compute='_compute_assset_count',
    )
    asset_count = fields.Integer(
        string='New Asset Count',
        compute='_compute_assset_count',
    )

    @api.multi
    def action_view_asset(self):
        self.ensure_one()
        old_asset = self._context.get('old_asset', False)
        action = self.env.ref('account_asset_management.account_asset_action')
        result = action.read()[0]
        asset_ids = []
        if old_asset:
            asset_ids = self.adjust_line_ids.mapped('asset_id').ids
        else:
            asset_ids = self.adjust_line_ids.mapped('ref_asset_id').ids
            asset_ids += \
                self.adjust_expense_to_asset_ids.mapped('ref_asset_id').ids
        dom = [('id', 'in', asset_ids)]
        result.update({'domain': dom})
        ctx = ast.literal_eval(result['context'])
        ctx.update({'active_test': False})
        result['context'] = ctx
        return result

    @api.multi
    @api.depends('adjust_line_ids', 'adjust_expense_to_asset_ids')
    def _compute_assset_count(self):
        for rec in self:
            # New
            asset_ids = self.adjust_line_ids.mapped('ref_asset_id').ids
            asset_ids += \
                self.adjust_expense_to_asset_ids.mapped('ref_asset_id').ids
            rec.asset_count = len(asset_ids)
            # Old
            old_asset_ids = self.adjust_line_ids.mapped('asset_id').ids
            old_asset_ids = \
                self.adjust_asset_to_expense_ids.mapped('asset_id').ids
            rec.old_asset_count = len(old_asset_ids)

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

    @api.model
    def get_invoice_line_assets(self, invoice):
        Asset = self.env['account.asset']
        invoice_lines = invoice.invoice_line
        if not invoice_lines:
            return False
        asset_lines = invoice_lines.filtered('product_id.asset')
        asset_moves = asset_lines.mapped('move_id')
        asset_picks = asset_moves.mapped('picking_id')
        assets = Asset.with_context(active_test=False).\
            search([('picking_id', 'in', asset_picks.ids)])
        return assets

    @api.onchange('adjust_type', 'invoice_id')
    def _onchange_adjust_type_invoice(self):
        self.adjust_line_ids = False
        self.adjust_asset_to_expense_ids = False
        self.adjust_expense_to_asset_ids = False
        if not self.invoice_id:
            return
        # Check if this adjustment is created from Suplier Invoice action
        src_invoice_id = self._context.get('default_invoice_id', False)
        if self.adjust_type == 'asset_type':
            assets = self.get_invoice_line_assets(self.invoice_id)
            values = self._context.get('adjust_asset_type_dict', {})
            for asset in assets:
                if src_invoice_id and str(asset.product_id.id) not in values:
                    continue
                adjust_line = self.env['account.asset.adjust.line'].new()
                adjust_line.asset_id = asset
                # adjust_line.date_remove = fields.Date.context_today(self)
                # STD-REMOVE
                # adjust_line._onchange_asset_id()
                # --
                # New Asset
                adjust_line.product_id = \
                    values and values[str(asset.product_id.id)] or False
                self.adjust_line_ids += adjust_line
        elif self.adjust_type == 'asset_to_expense':
            assets = self.get_invoice_line_assets(self.invoice_id)
            values = self._context.get('asset_to_expense_dict', {})
            for asset in assets:
                if src_invoice_id and str(asset.product_id.id) not in values:
                    continue
                adjust_line = \
                    self.env['account.asset.adjust.asset_to_expense'].new()
                adjust_line.asset_id = asset
                adjust_line.account_id = \
                    values and values[str(asset.product_id.id)] or False
                self.adjust_asset_to_expense_ids += adjust_line
        elif self.adjust_type == 'expense_to_asset':
            accounts = self.invoice_id.invoice_line.mapped('account_id')
            values = self._context.get('expense_to_asset_dict', {})
            for account in accounts:
                if src_invoice_id and str(account.id) not in values:
                    continue
                adjust_line = \
                    self.env['account.asset.adjust.expense_to_asset'].new()
                adjust_line.account_id = account
                adjust_line.product_id = \
                    values and values[str(account.id)][0] or False
                quantity = values and values[str(account.id)][1] or 1
                print adjust_line
                for i in range(quantity):
                    self.adjust_expense_to_asset_ids += adjust_line

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
        for line in self.adjust_line_ids.\
                filtered(lambda l: l.asset_id.state == 'open'):
            asset = line.asset_id
            asset.write({'status': line.target_status.id,
                         'state': 'removed',
                         'active': False})
            # Simple duplicate to new asset type, name
            new_asset = asset.copy({
                'profile_id': line.asset_profile_id.id,
                'product_id': line.product_id.id,
                'name': line.asset_name,
                'type': 'view',  # so it won't crate journal now.
                'purchase_id': False,
                'picking_id': False,
                'adjust_id': self.id,
                'active': True,
            })
            new_asset.type = 'normal'
            line.write({'ref_asset_id': new_asset.id})


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
        string='Origin Asset Item',
        required=True,
        domain=[('type', '!=', 'view'),
                ('profile_type', 'not in', ('ait', 'auc')),
                ('state', '=', 'open'),
                '|', ('active', '=', True), ('active', '=', False)],
        help="Asset to be removed, as it create new asset of the same value",
    )
    asset_state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Running'),
         ('close', 'Close'),
         ('removed', 'Removed')],
        string='Status',
        related='asset_id.state',
        readonly=True,
        store=True,
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
        string='New Asset Item',
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


class AccountAssetAdjustAssetToExpense(models.Model):
    _name = 'account.asset.adjust.asset_to_expense'

    adjust_id = fields.Many2one(
        'account.asset.adjust',
        string='Asset Adjust',
        index=True,
        ondelete='cascade',
    )
    asset_id = fields.Many2one(
        'account.asset',
        string='Origin Asset',
        required=True,
        domain=[('type', '!=', 'view'),
                ('profile_type', 'not in', ('ait', 'auc')),
                ('state', '=', 'open'),
                '|', ('active', '=', True), ('active', '=', False)],
        help="Asset to be removed, as it create new asset of the same value",
    )
    asset_state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Running'),
         ('close', 'Close'),
         ('removed', 'Removed')],
        string='Status',
        related='asset_id.state',
        readonly=True,
        store=True,
    )
    account_id = fields.Many2one(
        'account.account',
        string='Expense Account',
        required=True,
    )
    _sql_constraints = [
        ('asset_id_unique',
         'unique(asset_id, adjust_id)',
         'Duplicate assets selected!')
    ]


class AccountAssetAdjustExpenseToAsset(models.Model):
    _name = 'account.asset.adjust.expense_to_asset'

    adjust_id = fields.Many2one(
        'account.asset.adjust',
        string='Asset Adjust',
        index=True,
        ondelete='cascade',
    )
    account_id = fields.Many2one(
        'account.account',
        string='Expense Account',
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Asset Type',
        required=True,
        domain=[('asset', '=', True)],
        help="Asset to be removed, as it create new asset of the same value",
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
    amount = fields.Float(
        string='Asset Value',
        required=True,
    )
    ref_asset_id = fields.Many2one(
        'account.asset',
        string='New Asset',
        readonly=True,
    )
    _sql_constraints = [
        ('asset_id_unique',
         'unique(asset_id, adjust_id)',
         'Duplicate assets selected!'),
        ('positive_amount', 'check(amount > 0)',
         'Amount must be positive!')
    ]

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.asset_name = self.product_id.name
