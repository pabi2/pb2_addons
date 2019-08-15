# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountAssetRemoval(models.Model):
    _name = 'account.asset.removal'
    _inherit = ['mail.thread']
    _description = 'Asset Removal'
    _order = 'name desc'

    name = fields.Char(
        string='Name',
        default='/',
        required=True,
        readonly=True,
        copy=False,
        size=500,
    )
    date_remove = fields.Date(
        string='Removal Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        required=True,
        copy=False,
        readonly=True,
    )
    removal_asset_ids = fields.One2many(
        'account.asset.removal.line',
        'removal_id',
        string='Removing Assets',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Removed'),
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
        readonly=True,
        copy=False,
        track_visibility='onchange',
    )
    target_status = fields.Many2one(
        'account.asset.status',
        string='Asset Status',
        domain="[('map_state_removed', '=', 'removed')]",
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    target_status_code = fields.Char(
        string='Asset Status Code',
        related = 'target_status.code'
    )
    asset_count = fields.Integer(
        string='New Asset Count',
        compute='_compute_assset_count',
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        domain=[('asset', '=', True), ('analytic_journal_id', '=', False)],
        readonly=True,
        required=True,
        help="Asset Journal (No-Budget)",
    )
    deliver_to = fields.Char(
        string='Deliver to',
        size=500,
        help="If status is chagned to 'delivery', this field is required",
    )
    deliver_date = fields.Date(
        string='Delivery date',
        help="If status is chagned to 'delivery', this field is required",
    )

    @api.multi
    @api.depends('removal_asset_ids')
    def _compute_assset_count(self):
        for rec in self:
            ctx = {'active_test': False}
            # New
            asset_ids = self.removal_asset_ids.\
                with_context(ctx).mapped('asset_id').ids
            rec.asset_count = len(asset_ids)

    @api.model
    def default_get(self, field_list):
        res = super(AccountAssetRemoval, self).default_get(field_list)
        asset_ids = self._context.get('selected_asset_ids', [])
        user_id = self._context.get('default_user_id', False)
        target_status = self._context.get('default_target_status', False)
        asset_removal_lines = []
        for asset_id in asset_ids:
            Remove = self.env['account.asset.remove'].\
                with_context(active_id=asset_id)
            asset_removal_lines.append({
                'asset_id': asset_id,
                'user_id': user_id,
                'target_status': target_status,
                'sale_value': Remove._default_sale_value(),
                'account_sale_id': Remove._default_account_sale_id(),
                'account_plus_value_id':
                Remove._default_account_plus_value_id(),
                'account_min_value_id': Remove._default_account_min_value_id(),
                'account_residual_value_id':
                Remove._default_account_residual_value_id(),
                'posting_regime': Remove._get_posting_regime(),
            })
        res['removal_asset_ids'] = asset_removal_lines
        return res

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            Fiscal = self.env['account.fiscalyear']
            fiscalyear_id = Fiscal.find(vals.get('date_remove'))
            vals['name'] = self.env['ir.sequence'].\
                with_context(fiscalyear_id=fiscalyear_id).\
                get('account.asset.removal') or '/'
        return super(AccountAssetRemoval, self).create(vals)

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
        
    @api.multi
    def auto_post_account_move(self):
        Asset = self.env['account.asset']
        action = self.env.ref('account_asset_management.account_asset_action')
        for removal in self:
            asset_ids = removal.removal_asset_ids.mapped('asset_id').ids
            assets_id = Asset.with_context(active_test=False).search([('id', 'in',
                                                                    asset_ids)])
            
            for asset in assets_id:
                res = asset.open_entries()
                move_id = self.env['account.move'].search(res['domain'])
                for move in move_id:
                    if move.state == 'draft':
                        move.line_id._check_account_move_line2()
                        move.button_validate()

    @api.multi
    def _remove_confirmed_assets(self):
        for removal in self:
            if not removal.removal_asset_ids:
                raise ValidationError(_('No asset to remove!'))
            for line in removal.removal_asset_ids:
                if line.asset_id.state != 'open':
                    continue
                asset = line.asset_id
                ctx = {'active_ids': [asset.id], 'active_id': asset.id,
                       'overwrite_move_name': '/',
                       'overwrite_journal_id': removal.journal_id.id}
                if asset.value_residual and not asset.no_depreciation:
                    ctx.update({'early_removal': True})
                line.with_context(ctx).remove()
                asset.status = line.target_status

    @api.multi
    def action_done(self):
        for rec in self:
            assets = rec.removal_asset_ids.mapped('asset_id')
            if rec.target_status.code == 'deliver':
                for asset in assets:
                    asset.deliver_to = rec.deliver_to
                    asset.deliver_date = rec.deliver_date
            assets.validate_asset_to_removal()
            
        self._remove_confirmed_assets()
        self.write({'state': 'done'})
        self.auto_post_account_move()

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_view_asset(self):
        self.ensure_one()
        Asset = self.env['account.asset']
        action = self.env.ref('account_asset_management.account_asset_action')
        result = action.read()[0]
        asset_ids = self.removal_asset_ids.mapped('asset_id').ids
        assets = Asset.with_context(active_test=False).search([('id', 'in',
                                                                asset_ids)])
        dom = [('id', 'in', assets.ids)]
        result.update({'domain': dom})
        return result


class AccountAssetRemovalLine(models.Model):
    _name = 'account.asset.removal.line'
    _inherit = 'account.asset.remove'

    removal_id = fields.Many2one(
        'account.asset.removal',
        string='Removal ID',
        ondelete='cascade',
        index=True,
        readonly=True,
    )
    asset_id = fields.Many2one(
        'account.asset',
        string='Asset',
        domain=[('type', '=', 'normal'),
                ('state', '=', 'open')],
        required=True,
        ondelete='restrict',
    )
    target_status = fields.Many2one(
        'account.asset.status',
        string='Asset Status',
        domain="[('map_state_removed', '=', 'removed')]",
        required=True,
    )
    _sql_constraints = [
        ('asset_id_unique',
         'unique(asset_id, removal_id)',
         'Duplicate assets selected!')
    ]

    @api.onchange('asset_id')
    def _onchange_asset_id(self):
        Remove = self.env['account.asset.remove'].\
            with_context(active_id=self.asset_id.id)
        if self.asset_id:
            vals = Remove._get_sale()
            self.sale_value = vals['sale_value']
            self.account_sale_id = vals['account_sale_id']
            self.account_plus_value_id = \
                Remove._default_account_plus_value_id()
            self.account_min_value_id = \
                Remove._default_account_min_value_id()
            self.account_residual_value_id = \
                Remove._default_account_residual_value_id()
            self.posting_regime = Remove._get_posting_regime()

    @api.onchange('posting_regime')
    def _onchange_posting_regime(self):
        if self.posting_regime == 'residual_value' and not (self.account_residual_value_id):
            self.account_residual_value_id = self.env['account.account'].search([('code','=','5206060002')])