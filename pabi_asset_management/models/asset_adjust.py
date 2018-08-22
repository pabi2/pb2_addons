# -*- coding: utf-8 -*-
import ast
from openerp import models, fields, api, _
from openerp.addons.account_budget_activity_rpt.models.account_activity \
    import ActivityCommon
from openerp.addons.pabi_chartfield_merged.models.chartfield \
    import MergedChartField
from openerp.addons.pabi_chartfield.models.chartfield \
    import ChartFieldAction
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
    journal_id = fields.Many2one(
        'account.journal',
        string='Adjustment Journal',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        # default=lambda self: self._default_journal(),
        domain=[('asset', '=', True)],
    )
    date = fields.Date(
        string='Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_approve = fields.Date(
        string='Date Approved',
        required=False,
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
        [('asset_type', 'Asset => Assset'),
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
                ('state', 'in', ('open', 'paid')),
                ('asset_adjust_id', '=', False)],
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    source_document_type = fields.Selection(
        [('purchase', 'Purchase Order'),
         ('sale', 'Sales Order'),
         ('expense', 'Expense'),
         ('advance', 'Advance')],
        string='Source Document Type',
        related='invoice_id.source_document_type',
    )
    ship_purchase_id = fields.Many2one(
        'purchase.order',
        string='Ship Expense For PO',
        domain="[('order_type', '=', 'purchase_order'),"
        "('state', 'not in', ('draft', 'cancel'))]",
        help="This expense is shipping handling for things bought "
        "with this purchase order.",
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
    limit_asset_value = fields.Float(
        string='Limit Asset Value',
        help="Limit asset value for case Expense -> Asset",
    )
    limit_asset_value_readonly = fields.Float(
        string='Limit Asset Value',
        related='limit_asset_value',
        readonly=True,
        help="Limit asset value for case Expense -> Asset",
    )
    move_ids = fields.Many2many(
        'account.move',
        string='Journal Entries',
        compute='_compute_moves',
    )
    move_count = fields.Integer(
        string='JE Count',
        compute='_compute_moves',
    )

    @api.multi
    def _compute_moves(self):
        for rec in self:
            rec.move_ids = (
                rec.adjust_line_ids.mapped('move_id') or
                rec.adjust_expense_to_asset_ids.mapped('move_id') or
                rec.adjust_asset_to_expense_ids.mapped('move_id')
            ) + (
                rec.adjust_line_ids.mapped('cancel_move_id') or
                rec.adjust_expense_to_asset_ids.mapped('cancel_move_id') or
                rec.adjust_asset_to_expense_ids.mapped('cancel_move_id')
            )
            rec.move_count = len(rec.move_ids)
        return True

    # @api.model
    # def _default_journal(self):
    #     try:
    #         return self.env.ref('pabi_asset_management.journal_asset')
    #     except Exception:
    #         pass

    @api.multi
    def open_entries(self):
        self.ensure_one()
        return {
            'name': _("Journal Entries"),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': self._context,
            'nodestroy': True,
            'domain': [('id', 'in', self.move_ids.ids)],
        }

    @api.multi
    def action_view_asset(self):
        self.ensure_one()
        old_asset = self._context.get('old_asset', False)
        action = self.env.ref('account_asset_management.account_asset_action')
        result = action.read()[0]
        asset_ids = []
        if old_asset:
            asset_ids = self.adjust_line_ids.mapped('asset_id').ids
            asset_ids += \
                self.adjust_asset_to_expense_ids.mapped('asset_id').ids
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
    def _compute_assset_count(self):
        for rec in self:
            ctx = {'active_test': False}
            # New
            asset_ids = rec.adjust_line_ids.\
                with_context(ctx).mapped('ref_asset_id').ids
            asset_ids += rec.adjust_expense_to_asset_ids.\
                with_context(ctx).mapped('ref_asset_id').ids
            rec.asset_count = len(asset_ids)
            # Old
            old_asset_ids = rec.adjust_line_ids.\
                with_context(ctx).mapped('asset_id').ids
            old_asset_ids += rec.adjust_asset_to_expense_ids.\
                with_context(ctx).mapped('asset_id').ids
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
            if rec.adjust_type == 'asset_type':
                rec.adjust_asset_type()
            if rec.adjust_type == 'asset_to_expense':
                rec.adjust_asset_to_expense()
            if rec.adjust_type == 'expense_to_asset':
                rec.adjust_expense_to_asset()
            if not rec.date_approve:
                rec.date_approve = fields.Date.context_today(self)
            # Reference invoice back
            if rec.invoice_id:
                if rec.invoice_id.asset_adjust_id:
                    raise ValidationError(
                        _('Asset adjustment for %s already created!') %
                        rec.invoice_id.number)
                rec.invoice_id.asset_adjust_id = rec
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        """ Cancel for each case,
        1) Asset-Asset:
        2) Asset->Expense:
        3) Expense->Asset: reverse document + set new asset as removed
        """
        Status = self.env['account.asset.status']
        for rec in self:
            # 1) Asset -> Asset
            if rec.adjust_type == 'asset_type':
                adjust_lines = rec.adjust_line_ids
                for line in adjust_lines:
                    # Create reverse move
                    rev_move = self._create_reverse_entry(line.move_id)
                    line.cancel_move_id = rev_move
                    # Set back old asset
                    self._set_asset_as_restored(line.asset_id,
                                                line.origin_status)
                    # Remove new asset
                    target_status = Status.search([
                        ('code', '=', 'cancel')], limit=1)
                    self._set_asset_as_removed(line.ref_asset_id,
                                               target_status)
            # 2) Expense -> Asset
            if rec.adjust_type == 'asset_to_expense':
                adjust_lines = rec.adjust_asset_to_expense_ids
                for line in adjust_lines:
                    # Create reverse move
                    rev_move = self._create_reverse_entry(line.move_id)
                    line.cancel_move_id = rev_move
                    # Set back old asset
                    self._set_asset_as_restored(line.asset_id,
                                                line.origin_status)

            # 3) Expense -> Asset
            if rec.adjust_type == 'expense_to_asset':
                adjust_lines = rec.adjust_expense_to_asset_ids
                for line in adjust_lines:
                    # Create reverse move
                    rev_move = self._create_reverse_entry(line.move_id)
                    line.cancel_move_id = rev_move
                    # Remove asset
                    target_status = Status.search([
                        ('code', '=', 'cancel')], limit=1)
                    self._set_asset_as_removed(line.ref_asset_id,
                                               target_status)
            # Detach asset adjust from invoice, do it can create again.
            if rec.invoice_id:
                rec.invoice_id.write({'asset_adjust_id': False})
        self.write({'state': 'cancel'})

    @api.model
    def _create_reverse_entry(self, move):
        if not move:
            return False
        AccountMove = self.env['account.move']
        Period = self.env['account.period']
        move_dict = move.copy_data({
            'name': move.name + '_VOID',
            'ref': move.ref,
            'period_id': Period.find().id,
            'date': fields.Date.context_today(self),
            'reversal_id': move.id})[0]
        move_dict = AccountMove._switch_move_dict_dr_cr(move_dict)
        ctx = {'allow_asset': True}  # Allow linking asset, w/o create
        rev_move = AccountMove.with_context(ctx).create(move_dict)
        rev_move.button_validate()
        return rev_move

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
        status_cancel = self.env.ref('pabi_asset_management.'
                                     'asset_status_cancel')
        # Change Asset Type
        if self.adjust_type == 'asset_type':
            assets = self.get_invoice_line_assets(self.invoice_id)
            values = self._context.get('adjust_asset_type_dict', {})
            for asset in assets:
                if src_invoice_id and str(asset.product_id.id) not in values:
                    continue
                adjust_line = self.env['account.asset.adjust.line'].new()
                adjust_line.asset_id = asset
                adjust_line.target_status = status_cancel
                # New Asset
                adjust_line.product_id = \
                    values and values[str(asset.product_id.id)] or False
                adjust_line.asset_name = adjust_line.product_id.name
                # Budgeting
                adjust_line.section_id = asset.section_id
                adjust_line.project_id = asset.project_id
                adjust_line.invest_asset_id = asset.invest_asset_id
                adjust_line.invest_construction_phase_id = \
                    asset.invest_construction_phase_id
                # --
                self.adjust_line_ids += adjust_line
        # Asset => Expense
        elif self.adjust_type == 'asset_to_expense':
            assets = self.get_invoice_line_assets(self.invoice_id)
            values = self._context.get('asset_to_expense_dict', {})
            for asset in assets:
                if src_invoice_id and str(asset.product_id.id) not in values:
                    continue
                adjust_line = \
                    self.env['account.asset.adjust.asset_to_expense'].new()
                adjust_line.asset_id = asset
                adjust_line.target_status = status_cancel
                vals = values and values[str(asset.product_id.id)] or False
                adjust_line.account_id = vals and vals[0] or False
                adjust_line.activity_group_id = vals and vals[1] or False
                adjust_line.activity_id = vals and vals[2] or False
                # Budgeting
                adjust_line.section_id = asset.section_id
                adjust_line.project_id = asset.project_id
                adjust_line.invest_asset_id = asset.invest_asset_id
                adjust_line.invest_construction_phase_id = \
                    asset.invest_construction_phase_id
                # --
                self.adjust_asset_to_expense_ids += adjust_line
        # Expense => Asset
        elif self.adjust_type == 'expense_to_asset':
            if src_invoice_id:
                values = self._context.get('expense_to_asset_dict', {})
                for value in values:
                    adjust_line = \
                        self.env['account.asset.adjust.expense_to_asset'].new()
                    adjust_line.account_id = value[0]
                    adjust_line.product_id = value[1]
                    adjust_line.asset_name = adjust_line.product_id.name
                    adjust_line.invoice_line_id = value[2]
                    adjust_line.chartfield_id = \
                        adjust_line.invoice_line_id.chartfield_id
                    quantity = value[3]
                    for i in range(quantity):
                        self.adjust_expense_to_asset_ids += adjust_line
            else:
                accounts = self.invoice_id.invoice_line.\
                    filtered(lambda l: not l.product_id).mapped('account_id')
                for account in accounts:
                    adjust_line = \
                        self.env['account.asset.adjust.expense_to_asset'].new()
                    adjust_line.account_id = account
                    self.adjust_expense_to_asset_ids += adjust_line

    @api.model
    def _set_asset_as_removed(self, asset, target_status):
        self.ensure_one()
        # Set as removed and inactive
        asset.write({'status': target_status.id,
                     'state': 'removed',
                     'active': False})
        # Remove unposted lines
        depre_lines = asset.depreciation_line_ids
        depre_lines.filtered(
            lambda l: not (l.move_check or l.init_entry)).unlink()

    @api.model
    def _set_asset_as_restored(self, asset, origin_status):
        self.ensure_one()
        # Set as removed and inactive
        asset.write({'status': origin_status.id,
                     'state': 'open',
                     'active': True})
        # Recomput depreciatoin lines
        asset.compute_depreciation_board()

    @api.multi
    def _prepare_asset_dict(self, product, name, analytic):
        profile = product.asset_profile_id
        vals = {
            'profile_id': profile.id,
            'product_id': product.id,
            'name': name,
            # 'type': 'view', # so it won't create the first line journal entry
            'type': 'normal',
            'move_id': False,
            'adjust_id': self.id,
            'active': True,
            'status': False,
            'method': profile.method,
            'method_number': profile.method_number,
            'method_time': profile.method_time,
            'method_period': profile.method_period,
            'days_calc': profile.days_calc,
            'method_progress_factor': profile.method_progress_factor,
            'prorata': profile.prorata,
            'salvage_value': (not profile.no_depreciation and
                              profile.salvage_value or False),
            'account_analytic_id': False,  # Do not copy, product_id is changed
            # Dimension
            'section_id': analytic.section_id.id,
            'project_id': analytic.project_id.id,
            'invest_asset_id': analytic.invest_asset_id.id,
            'invest_construction_phase_id':
            analytic.invest_construction_phase_id.id,
        }
        return vals

    @api.model
    def _duplicate_asset(self, asset, product, asset_name, analytic):
        asset_dict = self._prepare_asset_dict(product, asset_name, analytic)
        new_asset = asset.copy(asset_dict)
        Analytic = self.env['account.analytic.account']
        new_asset.account_analytic_id = \
            Analytic.create_matched_analytic(new_asset)
        asset.target_asset_ids += new_asset
        # Set back to normal
        # new_asset.type = 'normal'
        # Also duplicate lines
        previous_id = False
        for line in asset.depreciation_line_ids.filtered(lambda l:
                                                         not l.init_entry):
            line = line.copy({'asset_id': new_asset.id,
                              'previous_id': line.previous_id and previous_id})
        return new_asset

    @api.model
    def _create_asset(self, asset_date, amount, product, asset_name, analytic):
        Asset = self.env['account.asset']
        Analytic = self.env['account.analytic.account']
        asset_dict = self._prepare_asset_dict(product, asset_name, analytic)
        asset_dict.update({'date_start': asset_date,
                           'purchase_value': amount,
                           })
        new_asset = Asset.create(asset_dict)
        new_asset.account_analytic_id = \
            Analytic.create_matched_analytic(new_asset)
        # Set back to normal
        # new_asset.type = 'normal'
        return new_asset

    @api.multi
    def adjust_asset_type(self):
        """ The Concept
        * Remove the origin asset (asset removal)
        * Create new type of asset (direct creation)
        * Create collective moves
        """
        self.ensure_one()
        Analytic = self.env['account.analytic.account']
        if not self.adjust_line_ids:
            raise ValidationError(_('No asset selected!'))
        # Check for AG/A
        if self.journal_id.analytic_journal_id:
            for line in self.adjust_line_ids:
                if not line.activity_rpt_id:
                    raise ValidationError(
                        _('AG/A is required for adjustment with budget'))
        for line in self.adjust_line_ids.\
                filtered(lambda l: l.asset_id.state == 'open'):
            line.account_analytic_id = \
                Analytic.create_matched_analytic(line)
            # Remove
            asset = line.asset_id
            self._set_asset_as_removed(asset, line.target_status)
            # Simple duplicate to new asset type, name
            new_asset = self._duplicate_asset(asset, line.product_id,
                                              line.asset_name,
                                              line.account_analytic_id)
            line.ref_asset_id = new_asset
            # Create a collective journal entry
            move = line.create_account_move_asset_type()
            line.move_id = move
            # Set move_check equal to amount depreciated
            new_asset.compute_depreciation_board()
            new_asset.validate()

    @api.multi
    def adjust_asset_to_expense(self):
        """ The Concept
        * Remove the origin asset (asset removal)
        * Create collective moves
        """
        self.ensure_one()
        Analytic = self.env['account.analytic.account']
        if not self.adjust_asset_to_expense_ids:
            raise ValidationError(_('No asset selected!'))
        # Check for AG/A
        if self.journal_id.analytic_journal_id:
            for line in self.adjust_asset_to_expense_ids:
                if not line.activity_id:
                    raise ValidationError(
                        _('AG/A is required for adjustment with budget'))
        for line in self.adjust_asset_to_expense_ids.\
                filtered(lambda l: l.asset_id.state == 'open'):
            line.account_analytic_id = \
                Analytic.create_matched_analytic(line)
            # Remove Assets
            asset = line.asset_id
            self._set_asset_as_removed(asset, line.target_status)
            # Adjustment's journal entry
            move = line.create_account_move_asset_to_expense()
            line.move_id = move

    @api.multi
    def adjust_expense_to_asset(self):
        """ The Concept
        * If ship_purchase_id is selected, set it to EX
        * Create new asset
        * Create collective moves
        """
        self.ensure_one()
        value = sum(self.adjust_expense_to_asset_ids.mapped('amount'))
        if float_compare(self.limit_asset_value, value, 2) == -1:
            raise ValidationError(_('Asset value exceed limit!'))
        Analytic = self.env['account.analytic.account']
        if not self.adjust_expense_to_asset_ids:
            raise ValidationError(_('No asset selected!'))
        # Check for AG/A
        if self.journal_id.analytic_journal_id:
            for line in self.adjust_expense_to_asset_ids:
                if not line.activity_rpt_id:
                    raise ValidationError(
                        _('AG/A is required for adjustment with budget'))
        # ship po
        if self.ship_purchase_id and self.source_document_type == 'expense':
            self.invoice_id.source_document_id.write({
                'ship_expense': True,
                'ship_purchase_id': self.ship_purchase_id.id, })
        # --
        for line in self.adjust_expense_to_asset_ids:
            line.account_analytic_id = \
                Analytic.create_matched_analytic(line)
            # Create new asset
            new_asset = self._create_asset(line.asset_date, line.amount,
                                           line.product_id, line.asset_name,
                                           line.account_analytic_id)
            line.ref_asset_id = new_asset
            # Find amount from depreciation board
            new_asset.compute_depreciation_board()
            new_asset.validate()
            depre_lines = new_asset.depreciation_line_ids.\
                filtered(lambda l: not l.init_entry and
                         l.line_date <= fields.Date.context_today(self))
            amount_depre = sum(depre_lines.mapped('amount'))
            # Create collective move
            move = line.create_account_move_expense_to_asset(amount_depre)
            line.move_id = move
            # Set move_check equal to amount depreciated
            depre_lines.write({'move_id': move.id})

    @api.model
    def _setup_move_data(self, journal, adjust_date,
                         period, ref):
        move_data = {
            'name': '/',
            'date': adjust_date,
            'ref': ref,
            'period_id': period.id,
            'journal_id': journal.id,
        }
        return move_data

    @api.model
    def _setup_move_line_data(self, name, asset, period, account, adjust_date,
                              debit=False, credit=False, analytic_id=False):
        if not debit and not credit:
            return False
        move_line_data = {
            'name': name,
            'ref': False,
            'account_id': account.id,
            'credit': credit,
            'debit': debit,
            'period_id': period.id,
            'partner_id': asset and asset.partner_id.id or False,
            'analytic_account_id': analytic_id,
            'date': adjust_date,
            'asset_id': asset and asset.id or False,
            'state': 'valid',
        }
        return move_line_data


class AccountAssetAdjustLine(MergedChartField, ActivityCommon,
                             ChartFieldAction, models.Model):
    _name = 'account.asset.adjust.line'
    _description = 'Asset to Asset'

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
                ('adjust_id', '=', False)],
        ondelete='restrict',
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
    origin_status = fields.Many2one(
        'account.asset.status',
        string='Origin Status',
        compute='_compute_origin_status',
        store=True,
        help="Status before being moved to expense, to be use when revert",
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
        ondelete='restrict',
    )
    target_status = fields.Many2one(
        'account.asset.status',
        string='Target Status',
        domain="[('map_state', 'in', ('removed', 'draft'))]",
        required=True,
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        copy=False,
    )
    cancel_move_id = fields.Many2one(
        'account.move',
        string='Cancel Journal Entry',
        readonly=True,
        copy=False,
    )
    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic',
        readonly=True,
    )
    _sql_constraints = [
        ('asset_id_unique',
         'unique(asset_id, adjust_id)',
         'Duplicate assets selected!')
    ]

    @api.multi
    @api.depends('asset_id')
    def _compute_origin_status(self):
        for rec in self:
            rec.origin_status = rec.asset_id.status
        return True

    @api.model
    def create(self, vals):
        asset = super(AccountAssetAdjustLine, self).create(vals)
        asset.update_related_dimension(vals)
        return asset

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.asset_name = self.product_id.name

    @api.multi
    def create_account_move_asset_type(self):
        """
        Dr: new asset - purchase value
            Cr: old asset - purchase value
        Dr: new - depre value (account_expense_depreciation_id) (budget)
        Dr: old - depre accum value (account_depreciation_id)
            Cr: new - depre accum value (account_depreciation_id)
            Cr: old - depre value (account_expense_depreciation_id) (budget)
        """
        self.ensure_one()
        AssetAdjust = self.env['account.asset.adjust']
        Period = self.env['account.period']
        adjust = self.adjust_id
        old_asset = self.asset_id
        new_asset = self.ref_asset_id
        adjust_date = adjust.date
        ctx = dict(self._context,
                   account_period_prefer_normal=True,
                   company_id=old_asset.company_id.id,
                   allow_asset=True, novalidate=True)
        period = Period.with_context(ctx).find(adjust_date)
        # Accountant want to use ref KV, EX
        # ref = '%s,%s' % (old_asset.name, new_asset.name)
        ref_docs = [adjust.name]
        if adjust.invoice_id:
            ref_docs.append(adjust.invoice_id.number)
        if adjust.ship_purchase_id:
            ref_docs.append(adjust.ship_purchase_id.name)
        ref = ', '.join(ref_docs)
        # --
        am_vals = AssetAdjust._setup_move_data(adjust.journal_id,
                                               adjust_date, period, ref)
        move = self.env['account.move'].with_context(ctx).create(am_vals)
        # Prepare move lines
        line_dict = self._prepare_move_line_asset_type(old_asset, new_asset,
                                                       period, adjust_date)
        move.write({'line_id': line_dict})
        if adjust.journal_id.entry_posted:
            del ctx['novalidate']
            move.with_context(ctx).post()
        return move

    @api.model
    def _prepare_move_line_asset_type(self, old_asset, new_asset,
                                      period, adjust_date):
        """
        Cases from asset to asset
            * Asset to Asset
            * LV Asset to Asset (no depre on old asset)
            * Asset to LV Asset (no depre on new asset)
        """
        line_dict = []
        AssetAdjust = self.env['account.asset.adjust']
        old_asset_acc = old_asset.profile_id.account_asset_id
        new_asset_acc = new_asset.profile_id.account_asset_id
        old_depr_acc = old_asset.profile_id.account_depreciation_id
        new_depr_acc = new_asset.profile_id.account_depreciation_id
        old_exp_acc = old_asset.profile_id.account_expense_depreciation_id
        new_exp_acc = new_asset.profile_id.account_expense_depreciation_id
        # Dr: new asset - asset value
        #     Cr: old asset - asset value
        purchase_value = old_asset.purchase_value
        if purchase_value:
            new_asset_debit = AssetAdjust._setup_move_line_data(
                new_asset.code, new_asset, period, new_asset_acc, adjust_date,
                debit=purchase_value, credit=False,
                analytic_id=new_asset.account_analytic_id.id)
            old_asset_credit = AssetAdjust._setup_move_line_data(
                old_asset.code, old_asset, period, old_asset_acc, adjust_date,
                debit=False, credit=purchase_value,
                analytic_id=old_asset.account_analytic_id.id)
            line_dict += [(0, 0, new_asset_debit), (0, 0, old_asset_credit)]
        # Dr: old - depre accum value (account_depreciation_id)
        #   Cr: old - depre value (account_expense_depreciation_id)(budget)
        # Dr: new - depre value (account_expense_depreciation_id)(budget)
        #   Cr: new - depre accum value (account_depreciation_id)
        amount_depre = old_asset.value_depreciated
        # Old
        if amount_depre and not old_asset.profile_id.no_depreciation:
            old_depre_debit = AssetAdjust._setup_move_line_data(
                old_asset.code, old_asset, period, old_depr_acc, adjust_date,
                debit=amount_depre, credit=False, analytic_id=False)
            old_exp_credit = AssetAdjust._setup_move_line_data(
                old_asset.code, old_asset, period, old_exp_acc, adjust_date,
                debit=False, credit=amount_depre,
                analytic_id=old_asset.account_analytic_id.id)
            line_dict += [(0, 0, old_depre_debit), (0, 0, old_exp_credit), ]
        # New
        if amount_depre and not new_asset.profile_id.no_depreciation:
            new_depre_debit = AssetAdjust._setup_move_line_data(
                new_asset.code, new_asset, period, new_exp_acc, adjust_date,
                debit=amount_depre, credit=False,
                analytic_id=new_asset.account_analytic_id.id)
            new_exp_credit = AssetAdjust._setup_move_line_data(
                new_asset.code, new_asset, period, new_depr_acc, adjust_date,
                debit=False, credit=amount_depre, analytic_id=False)
            line_dict += [(0, 0, new_depre_debit), (0, 0, new_exp_credit), ]
        return line_dict


class AccountAssetAdjustAssetToExpense(MergedChartField, ActivityCommon,
                                       ChartFieldAction, models.Model):
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
        ondelete='restrict',
        domain=[('type', '!=', 'view'),
                ('profile_type', 'not in', ('ait', 'auc')),
                ('state', '=', 'open'),
                '|', ('active', '=', True), ('active', '=', False)],
        help="Asset to be removed, as it create new asset of the same value",
    )
    name = fields.Char(
        string='Description',
        help="Description to be shown in journal entry."
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
    origin_status = fields.Many2one(
        'account.asset.status',
        string='Origin Status',
        compute='_compute_origin_status',
        store=True,
        help="Status before being moved to expense, to be use when revert",
    )
    target_status = fields.Many2one(
        'account.asset.status',
        string='Target Status',
        domain="[('map_state', 'in', ('removed', 'draft'))]",
        required=True,
    )
    account_id = fields.Many2one(
        'account.account',
        string='Expense Account',
        required=True,
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        copy=False,
    )
    cancel_move_id = fields.Many2one(
        'account.move',
        string='Cancel Journal Entry',
        readonly=True,
        copy=False,
    )
    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic',
        readonly=True,
    )
    _sql_constraints = [
        ('asset_id_unique',
         'unique(asset_id, adjust_id)',
         'Duplicate assets selected!')
    ]

    @api.multi
    @api.depends('asset_id')
    def _compute_origin_status(self):
        for rec in self:
            rec.origin_status = rec.asset_id.status
        return True

    @api.model
    def create(self, vals):
        asset = super(AccountAssetAdjustAssetToExpense, self).create(vals)
        asset.update_related_dimension(vals)
        return asset

    @api.multi
    def create_account_move_asset_to_expense(self):
        """
        Dr: expense - purchase value
            Cr: old asset - purchase value
        Dr: old - depre accum value (account_depreciation_id)
            Cr: old - depre value (account_expense_depreciation_id) (budget)
        """
        self.ensure_one()
        AssetAdjust = self.env['account.asset.adjust']
        Period = self.env['account.period']
        adjust = self.adjust_id
        old_asset = self.asset_id
        exp_acc = self.account_id
        adjust_date = adjust.date
        ctx = dict(self._context,
                   account_period_prefer_normal=True,
                   company_id=old_asset.company_id.id,
                   allow_asset=True, novalidate=True)
        period = Period.with_context(ctx).find(adjust_date)
        # ref = old_asset.name
        ref_docs = [adjust.name]
        if adjust.invoice_id:
            ref_docs.append(adjust.invoice_id.number)
        if adjust.ship_purchase_id:
            ref_docs.append(adjust.ship_purchase_id.name)
        ref = ', '.join(ref_docs)
        # --
        am_vals = AssetAdjust._setup_move_data(adjust.journal_id,
                                               adjust_date, period, ref)
        move = self.env['account.move'].with_context(ctx).create(am_vals)
        # Prepare move lines
        line_dict = \
            self._prepare_move_line_asset_to_expense(old_asset, exp_acc,
                                                     period, adjust_date)
        move.write({'line_id': line_dict})
        if adjust.journal_id.entry_posted:
            del ctx['novalidate']
            move.with_context(ctx).post()
        self.write({'move_id': move.id})
        return move

    @api.model
    def _prepare_move_line_asset_to_expense(self, old_asset, exp_acc,
                                            period, adjust_date):
        line_dict = []
        AssetAdjust = self.env['account.asset.adjust']
        old_asset_acc = old_asset.profile_id.account_asset_id
        old_depr_acc = old_asset.profile_id.account_depreciation_id
        old_exp_acc = old_asset.profile_id.account_expense_depreciation_id
        # Dr: expense - asset value
        #     Cr: old asset - asset value
        purchase_value = old_asset.purchase_value
        if purchase_value:
            expense_debit = AssetAdjust._setup_move_line_data(
                self.name or exp_acc.name, False, period, exp_acc, adjust_date,
                debit=purchase_value, credit=False,
                analytic_id=self.account_analytic_id.id)
            old_asset_credit = AssetAdjust._setup_move_line_data(
                old_asset.code, old_asset, period, old_asset_acc, adjust_date,
                debit=False, credit=purchase_value,
                analytic_id=False)
            line_dict += [(0, 0, expense_debit), (0, 0, old_asset_credit)]
        # Dr: old - depre accum value (account_depreciation_id)
        #   Cr: old - depre value (account_expense_depreciation_id)(budget)
        amount_depre = old_asset.value_depreciated
        # Old
        if amount_depre and not old_asset.profile_id.no_depreciation:
            old_depre_debit = AssetAdjust._setup_move_line_data(
                old_asset.code, old_asset, period, old_depr_acc, adjust_date,
                debit=amount_depre, credit=False, analytic_id=False)
            old_exp_credit = AssetAdjust._setup_move_line_data(
                old_asset.code, old_asset, period, old_exp_acc, adjust_date,
                debit=False, credit=amount_depre,
                analytic_id=old_asset.account_analytic_id.id)
            line_dict += [(0, 0, old_depre_debit), (0, 0, old_exp_credit), ]
        return line_dict


class AccountAssetAdjustExpenseToAsset(MergedChartField, ActivityCommon,
                                       ChartFieldAction, models.Model):
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
    asset_date = fields.Date(
        string='Asset Start Date',
        required=True,
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
    invoice_line_id = fields.Many2one(
        'account.invoice.line',
        string='Invoice Line',
    )
    ref_asset_id = fields.Many2one(
        'account.asset',
        string='New Asset',
        readonly=True,
        ondelete='restrict',
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        copy=False,
    )
    cancel_move_id = fields.Many2one(
        'account.move',
        string='Cancel Journal Entry',
        readonly=True,
        copy=False,
    )
    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic',
        readonly=True,
    )
    _sql_constraints = [
        ('asset_id_unique',
         'unique(asset_id, adjust_id)',
         'Duplicate assets selected!'),
        ('positive_amount', 'check(amount > 0)',
         'Amount must be positive!')
    ]

    @api.model
    def create(self, vals):
        asset = super(AccountAssetAdjustExpenseToAsset, self).create(vals)
        asset.update_related_dimension(vals)
        return asset

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.asset_name = self.product_id.name

    @api.multi
    def create_account_move_expense_to_asset(self, amount_depre):
        """
        Dr: new asset - expense value
            Cr: expense - expense value
        Dr: new - depre (account_expense_depreciation_id) (budget)
            Cr: new - depre accum (account_depreciation_id)
        """
        self.ensure_one()
        AssetAdjust = self.env['account.asset.adjust']
        Period = self.env['account.period']
        adjust = self.adjust_id
        new_asset = self.ref_asset_id
        exp_acc = self.account_id
        adjust_date = adjust.date
        ctx = dict(self._context,
                   account_period_prefer_normal=True,
                   company_id=new_asset.company_id.id,
                   allow_asset=True, novalidate=True)
        period = Period.with_context(ctx).find(adjust_date)
        # ref = self.asset_name
        ref_docs = [adjust.name]
        if adjust.invoice_id:
            ref_docs.append(adjust.invoice_id.number)
        if adjust.ship_purchase_id:
            ref_docs.append(adjust.ship_purchase_id.name)
        ref = ', '.join(ref_docs)
        # --
        am_vals = AssetAdjust._setup_move_data(adjust.journal_id,
                                               adjust_date, period, ref)
        move = self.env['account.move'].with_context(ctx).create(am_vals)
        # Prepare move lines
        line_dict = \
            self._prepare_move_line_expense_to_asset(new_asset, exp_acc,
                                                     period, adjust_date,
                                                     amount_depre)
        move.write({'line_id': line_dict})
        if adjust.journal_id.entry_posted:
            del ctx['novalidate']
            move.with_context(ctx).post()
        self.write({'move_id': move.id})
        return move

    @api.model
    def _prepare_move_line_expense_to_asset(self, new_asset, exp_acc,
                                            period, adjust_date,
                                            amount_depre):
        line_dict = []
        AssetAdjust = self.env['account.asset.adjust']
        new_asset_acc = new_asset.profile_id.account_asset_id
        new_depr_acc = new_asset.profile_id.account_depreciation_id
        new_exp_acc = new_asset.profile_id.account_expense_depreciation_id
        # Dr: new asset - asset value
        #     Cr: expense - asset value
        purchase_value = new_asset.purchase_value
        if purchase_value:
            new_asset_debit = AssetAdjust._setup_move_line_data(
                new_asset.code, new_asset, period, new_asset_acc, adjust_date,
                debit=purchase_value, credit=False,
                analytic_id=False)
            expenese_credit = AssetAdjust._setup_move_line_data(
                exp_acc.name, False, period, exp_acc, adjust_date,
                debit=False, credit=purchase_value,
                analytic_id=new_asset.account_analytic_id.id)
            line_dict += [(0, 0, new_asset_debit), (0, 0, expenese_credit)]
        # Dr: new - depre value (account_expense_depreciation_id)(budget)
        #   Cr: new - depre accum value (account_depreciation_id)
        if amount_depre and not new_asset.profile_id.no_depreciation:
            new_exp_debit = AssetAdjust._setup_move_line_data(
                new_asset.code, new_asset, period, new_exp_acc, adjust_date,
                debit=amount_depre, credit=False,
                analytic_id=new_asset.account_analytic_id.id)
            new_depr_credit = AssetAdjust._setup_move_line_data(
                new_asset.code, new_asset, period, new_depr_acc, adjust_date,
                debit=False, credit=amount_depre,
                analytic_id=False)
            line_dict += [(0, 0, new_exp_debit), (0, 0, new_depr_credit), ]
        return line_dict
