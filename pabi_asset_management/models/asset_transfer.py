# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare
import logging

_logger = logging.getLogger(__name__)


class AccountAssetTransfer(models.Model):
    _name = 'account.asset.transfer'
    _inherit = ['mail.thread']
    _description = 'Asset Transfer'
    _order = 'name desc'

    name = fields.Char(
        string='Name',
        default='/',
        required=True,
        readonly=True,
        copy=False,
        size=500,
    )
    date = fields.Date(
        string='Transfer Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
        copy=False,
        readonly=True,
        states={'draft2': [('readonly', False)]},
        help="This date will be used as accouning date for the new asset.\n"
        "It must be within this same month."
    )
    date_accept = fields.Date(
        string='Commitee Accept Date',
        required=True,
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)],
                'draft2': [('readonly', False)]},
        help="If accept date not equal to transfer date, a reason is needed."
    )
    date_diff = fields.Boolean(
        string='Date Diff',
        compute='_compute_date_diff',
    )
    reason = fields.Char(
        string='Reason',
        readonly=True,
        states={'draft': [('readonly', False)],
                'draft2': [('readonly', False)]},
        size=500,
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
        size=1000,
    )
    asset_ids = fields.Many2many(
        'account.asset',
        'account_asset_transfer_rel',
        'transfer_id', 'asset_id',
        string='Source Assets',
        domain=[('type', '!=', 'view'),
                ('profile_type', 'in', ('normal','ait','auc','atm','lva')),
                '|', ('active', '=', True), ('active', '=', False)],
        copy=True,
        readonly=True,
        ondelete='restrict',
        states={'draft': [('readonly', False)]},
    )
    target_asset_ids = fields.One2many(
        'account.asset.transfer.target',
        'transfer_id',
        string='Target New Assets',
        copy=True,
        readonly=True,
        states={'draft2': [('readonly', False)]},
    )
    transfer_type = fields.Selection(
        [('merge', 'Merge (many source -> 1 target)'),
         ('split', 'Split (1 source -> many target)'),
         ('transfer', 'Transfer (many source -> many target)')],
        string='Transfer Type',
        compute='_compute_transfer_type',
        store=True,
    )
    state = fields.Selection(
        [('draft', 'Source Assets'),
         ('draft2', 'Target Assets'),
         ('ready', 'Ready'),
         ('done', 'Transferred'),
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
        readonly=True,
        copy=False,
        track_visibility='onchange',
    )
    source_asset_value = fields.Float(
        string='Source Asset Value',
        compute='_compute_asset_value',
    )
    target_asset_value = fields.Float(
        string='Target Asset Value',
        compute='_compute_asset_value',
    )
    target_asset_count = fields.Integer(
        string='Source Asset Count',
        compute='_compute_asset_count',
    )
    new_asset_ids = fields.Many2many(
        'account.asset',
        'asset_transfer_asset_rel',
        'transfer_id', 'asset_id',
        string='New Assets',
        readonly=True,
    )
    source_asset_count = fields.Integer(
        string='Source Asset Count',
        compute='_compute_asset_count',
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        domain=[('asset', '=', True), ('analytic_journal_id', '=', False)],
        readonly=True,
        required=True,
        help="Asset Journal (No-Budget)",
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entries',
        readonly=True,
    )
    # move_ids = fields.Many2many(
    #     'account.move',
    #     string='Journal Entries',
    #     compute='_compute_moves',
    # )
    # move_count = fields.Integer(
    #     string='JE Count',
    #     compute='_compute_moves',
    # )
    #
    # @api.multi
    # def _compute_moves(self):
    #     for rec in self:
    #         rec.move_ids = rec.target_asset_ids.mapped('move_id')
    #         rec.move_count = len(rec.move_ids)
    #     return True

    @api.multi
    def _compute_asset_count(self):
        for rec in self:
            rec.source_asset_count = len(rec.asset_ids)
            rec.target_asset_count = len(rec.new_asset_ids)

    @api.multi
    @api.depends('date', 'date_accept')
    def _compute_date_diff(self):
        for rec in self:
            if rec.date and rec.date_accept:
                rec.date_diff = rec.date != rec.date_accept
            else:
                rec.date_diff = False

    @api.multi
    @api.constrains('date', 'date_accept')
    def _check_date(self):
        Period = self.env['account.period']
        for rec in self:
            # If date diff, need readon
            if rec.date != rec.date_accept and not rec.reason:
                raise ValidationError(
                    _('Accept date and transfer date is different, '
                      'please provide a reason!'))
            if Period.find(dt=rec.date) != Period.find():
                raise ValidationError(
                    _('Transfer date must be within current period!'))

    @api.onchange('date', 'date_accept')
    def _onchange_date(self):
        if self.date == self.date_accept:
            self.reason = False

    @api.multi
    def _validate_asset_values(self):
        for rec in self:
            if not rec.asset_ids or not rec.target_asset_ids:
                raise ValidationError(_('Source or target assets not filled!'))
            inactive_assets = rec.asset_ids.filtered(lambda l: not l.active)
            if inactive_assets:
                names = ', '.join(inactive_assets.mapped('code'))
                raise ValidationError(
                    _('Following assets are not active!\n%s') % names)
            if float_compare(rec.source_asset_value,
                             rec.target_asset_value, 2) != 0:
                raise ValidationError(
                    _('To transfer, source and target value must equal!'))

    @api.multi
    @api.depends('asset_ids', 'target_asset_ids')
    def _compute_asset_value(self):
        for rec in self:
            source_value = \
                sum(rec.asset_ids.mapped('purchase_value'))
            target_value = \
                sum(rec.target_asset_ids.mapped('depreciation_base'))
            rec.source_asset_value = source_value
            rec.target_asset_value = target_value

    @api.multi
    @api.depends('asset_ids', 'target_asset_ids')
    def _compute_transfer_type(self):
        """ 2 case allowed, 1) merget 2) split """
        for rec in self:
            if not rec.asset_ids or not rec.target_asset_ids:
                rec.trasferring = False
            elif len(rec.asset_ids) == 1 and len(rec.target_asset_ids) >= 1:
                rec.transfer_type = 'split'
            elif len(rec.asset_ids) >= 1 and len(rec.target_asset_ids) == 1:
                rec.transfer_type = 'merge'
            elif len(rec.asset_ids) > 1 and len(rec.target_asset_ids) > 1:
                rec.transfer_type = 'transfer'
            else:
                raise ValidationError(
                    _('You set up source/target assets incorrectly,\nonly '
                      'split (1-M), merge (M-1), transfer (M-M) is allowed!'))

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].\
                get('account.asset.transfer') or '/'
        return super(AccountAssetTransfer, self).create(vals)

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_draft2(self):
        self.write({'state': 'draft2'})

    @api.multi
    def action_ready(self):
        for rec in self:
            rec._validate_asset_values()
        self.write({'state': 'ready'})

    @api.multi
    def action_done(self):
        for rec in self:
            rec._validate_asset_values()
            rec._transfer_new_asset()
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    # @api.multi
    # def _transfer_new_asset(self):
    #     """ The Concept
    #     * A new asset will be created, owner chartfields will be the same
    #       * So, make sure that the asset_profile_id only on new move
#     * All source asset must have same owner chartfields, otherwise, warning
#     * We code to allow transfering the asset with depre, in fact, it won't
    #     * Inactive source assets
    #     Account Moves
    #     =============
#     Dr Accumulated depreciation of transfer assets (for each asset, if any)
    #         Cr Asset Value of trasferring assets (for each asset)
    #     Dr Asset Value to the new asset
    #         Cr Accumulated Depreciation of to the new asset (if any)
    #     """
    #     self.ensure_one()
    #     AccountMove = self.env['account.move']
    #     Asset = self.env['account.asset']
    #     Period = self.env['account.period']
    #     AssetStatus = self.env['account.asset.status']
    #     period = Period.find()
    #     # Owner
    #     project = self.asset_ids.mapped('project_id')
    #     section = self.asset_ids.mapped('section_id')
    #     # For Transfer, all asset must belong to same owner
    #     if len(project) > 1 or len(section) > 1:
    #         raise ValidationError(
    #             _('When transfer to new asset, all selected '
    #               'assets must belong to same owner!'))
    #     new_owner = {'owner_project_id': project.id,
    #                  'owner_section_id': section.id}
    #     # Purchase method, when mixed -> อื่นๆ (asset_purchase_method_11)
    #     purchase_methods = self.asset_ids.mapped('asset_purchase_method_id')
    #     new_purchase_method = (len(purchase_methods) == 1 and
    #                            purchase_methods[0] or
    #                            self.env.ref('pabi_asset_management.'
    #                                         'asset_purchase_method_11'))
    #     # Prepare Old Move
    #     asset_move_lines_dict, depre_move_lines = \
    #         Asset._prepare_asset_reverse_moves(self.asset_ids)
    #     # Create move line for target asset
    #     new_asset_move_line_dict = \
    #         Asset._prepare_asset_target_move(asset_move_lines_dict,
    #                                          new_owner=new_owner)
    #     new_asset_ids = []
    #     count = len(self.target_asset_ids)
    #     total_depre = sum([x['debit'] for x in depre_move_lines])
    #     accum_depre = 0.0
    #     i = 0
    #     for target_asset in self.target_asset_ids:
    #         i += 1
    #         # Ratio
    #         ratio = 1.0
    #         if self.source_asset_value:
    #             ratio = (target_asset.depreciation_base /
    #                      self.source_asset_value)
    #         # For each target asset, start with reverse move
    #         move_lines = list(asset_move_lines_dict)
    #         # Property of New Asset
    #         new_product = target_asset.product_id
    #         new_asset_profile = new_product.asset_profile_id
    #         # Force to AN before lek think it should be fixed.
    #         # new_journal = new_asset_profile.journal_id
    #         new_journal = self.journal_id
    #         new_account_asset = new_asset_profile.account_asset_id
    #         # For transfer, for each new asset, update following fields
    #         new_asset_move_line_dict.update({
    #             'name': target_asset.asset_name,
    #             'product_id': new_product.id,
    #             'asset_profile_id': new_asset_profile.id,
    #             'account_id': new_account_asset.id,
    #         })
    #         move_lines.append(new_asset_move_line_dict)
    #         for move_line in move_lines:
    #             move_line['debit'] = move_line['debit'] and \
    #                 target_asset.depreciation_base or 0.0
    #             move_line['credit'] = move_line['credit'] and \
    #                 target_asset.depreciation_base or 0.0
    #         # Depreciation Move Line
    #         if depre_move_lines:
    #             depre_move_lines = list(depre_move_lines)
    #             new_depre_dict = \
    #                 Asset._prepare_asset_target_move(depre_move_lines)
    #             depre_move_lines.append(new_depre_dict)
    #             new_depre = 0.0
    #             if i == count:
    #                 new_depre = total_depre - accum_depre
    #             else:
    #                 new_depre = ratio * total_depre
    #             for move_line in depre_move_lines:
    #                 move_line['debit'] = \
    #                     move_line['debit'] and new_depre or 0.0
    #                 move_line['credit'] = \
    #                     move_line['credit'] and new_depre or 0.0
    #             accum_depre += new_depre
    #             move_lines += depre_move_lines
    #         # For transfer case, make sure that asset_id is false
    #         for x in move_lines:
    #             x.update({'asset_id': False})
    #         # Finalize all moves before create it.
    #         final_move_lines = [(0, 0, x) for x in move_lines]
    #         move_dict = {'journal_id': new_journal.id,
    #                      'line_id': final_move_lines,
    #                      'period_id': period.id,
    #                      'date': self.date,
    #                      'ref': self.name}
    #         ctx = {'asset_purchase_method_id': new_purchase_method.id,
    #             'direct_create': False}  # direct_create to recalc dimension
    #         move = AccountMove.with_context(ctx).create(move_dict)
    #         # For transfer, new asset should be created
    #         asset = move.line_id.mapped('asset_id')
    #         if len(asset) != 1:
    #             raise ValidationError(
    #                 _('An asset should be created, something went wrong!'))
    #         new_asset_ids.append(asset.id)
    #         target_asset.write({'ref_asset_id': asset.id,
    #                             'move_id': move.id})
    #         asset.source_asset_ids = self.asset_ids
    #     self.asset_ids.write({
    #         'active': False,
    #         'target_asset_ids': [(4, x) for x in new_asset_ids],
    #         'status': AssetStatus.search([('code', '=', 'transfer')]).id})

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
            'period_id': period,
            'partner_id': asset and asset.partner_id.id or False,
            'analytic_account_id': analytic_id,
            'date': adjust_date,
            'asset_id': asset and asset.id or False,
            'state': 'valid',
        }
        return move_line_data

    @api.model
    def _prepare_move_line_asset(self, asset, period, adjust_date):
        line_dict = []
        asset_account = asset.profile_id.account_asset_id
        depreciation_base = asset.depreciation_base
        amount_depre = asset.value_depreciated
        removal_amount = depreciation_base - amount_depre
        # first asset line
        asset_debit = self._setup_move_line_data(
            asset.code, asset, period, asset_account, adjust_date,
            debit=removal_amount, credit=False,
            analytic_id=asset.account_analytic_id.id)
        # last asset line
        asset_credit = self._setup_move_line_data(
            asset.code, asset, period, asset_account, adjust_date,
            debit=False, credit=depreciation_base,
            analytic_id=asset.account_analytic_id.id)
        line_dict += [(0, 0, asset_debit), (0, 0, asset_credit)]

        # Accumulated
        if amount_depre and not asset.profile_id.no_depreciation:
            asset_debit = self._setup_move_line_data(
                asset.code, asset, period, asset_account, adjust_date,
                debit=amount_depre, credit=False,
                analytic_id=asset.account_analytic_id.id)
            line_dict += [(0, 0, asset_debit)]
        return line_dict

    @api.multi
    def _remove_asset_line(self, asset):
        # check condition create line
        ctx = {}
        move_obj = self.env['account.move']
        period_obj = self.env['account.period']
        asset_line_obj = self.env['account.asset.line']
        digits = self.env['decimal.precision'].precision_get('Account')
        date_bf_remove = \
            (fields.Date.from_string(self.date) - relativedelta(days=1))
        date_bf_remove = fields.Date.to_string(date_bf_remove)
        days = sum(asset.depreciation_line_ids.mapped('line_days'))
        day_amount = round(asset.depreciation_base / days, digits)
        # Remove unposted lines
        depre_lines = asset.depreciation_line_ids
        depre_lines.filtered(
            lambda l: not (l.move_check or l.init_entry)).unlink()

        running_asset = asset.depreciation_line_ids.filtered(
            lambda l: l.type == 'depreciate')
        lines = 2
        if asset.depreciation_line_ids[-1].line_date == date_bf_remove:
            lines = 1
        for val in range(lines):
            dlines = asset.depreciation_line_ids
            # find days in line
            line_date = fields.Date.from_string(self.date)
            last_asset_line = fields.Date.from_string(dlines[-1].line_date)
            line_name = asset._get_depreciation_entry_name(len(dlines))
            # create before last asset line
            if val == 0 and lines == 2:
                line_date = (line_date - relativedelta(days=1))
                days = (line_date - last_asset_line).days
                # find amount in line per days
                amount = days * day_amount
            # removal line
            if (val == 1 and lines == 2) or lines == 1:
                days = (line_date - last_asset_line).days - 1
                amount = dlines[0].amount_accumulated - \
                    dlines[-1].amount_accumulated
                # Create a collective journal entry
                ctx.update(account_period_prefer_normal=True)
                period_ids = period_obj.with_context(
                    ctx).find(self.date)
                period_id = period_ids[0].id
                journal_id = asset.profile_id.journal_id.id
                move_vals = {
                    'name': asset.name,
                    'date': self.date,
                    'ref': line_name,
                    'period_id': period_id,
                    'journal_id': journal_id,
                    'narration': self.note,
                }
                move = move_obj.create(move_vals)
                move_lines = self._prepare_move_line_asset(
                    asset, period_id, self.date)
                move.with_context(allow_asset=True).write(
                    {'line_id': move_lines})
                # Auto post
                move.button_validate()
            if lines == 1:
                amount = dlines[0].amount_accumulated

            line_date = fields.Date.to_string(line_date)
            asset_line_vals = {
                'previous_id': dlines[-1].id,
                'amount': amount,
                'asset_id': asset.id,
                'name': line_name,
                'line_date': line_date,
                'line_days': days,
                'move_id': move.id if line_date == self.date
                else False,
                'type': 'remove' if line_date == self.date
                else 'depreciate',
            }
            asset_line = asset_line_obj.create(asset_line_vals)
            # Check asset line never post
            if not running_asset:
                ctx = {'allow_asset_line_update': True}
                asset_line.with_context(ctx).depreciated_value = 0.0
                asset_line.with_context(ctx).amount_accumulated = amount
            # Auto post before last asset line
            if val == 0 and lines == 2:
                move_before_last_id = asset_line.create_move()
                # Auto post
                move_obj.browse(move_before_last_id).post()

    @api.multi
    def _transfer_new_asset(self):
        """ The Concept
        * A new asset will be created, owner chartfields will be the same
          * So, make sure that the asset_profile_id only on new move
        * All source asset must have same owner chartfields, otherwise, warning
        * We code to allow transfering the asset with depre, in fact, it won't
        * Inactive source assets
        Account Moves
        =============
        Dr Accumulated depreciation of transfer assets (for each asset, if any)
            Cr Asset Value of trasferring assets (for each asset)
        Dr Asset Value to the new asset
            Cr Accumulated Depreciation of to the new asset (if any)
        """
        self.ensure_one()
        AccountMove = self.env['account.move']
        Period = self.env['account.period']
        AssetStatus = self.env['account.asset.status']
        # Owner
        project = self.asset_ids.mapped('owner_project_id')
        section = self.asset_ids.mapped('owner_section_id')
        invest_asset = self.asset_ids.mapped('owner_invest_asset_id')
        invest_construction_phase = \
            self.asset_ids.mapped('owner_invest_construction_phase_id')
        # For Transfer, all asset must belong to same owner
        if len(project) + len(section) + len(invest_asset) + \
                len(invest_construction_phase) > 1:
            raise ValidationError(
                _('When transfer to new asset, all selected '
                  'assets must belong to same budget owner!'))
        # Purchase method, when mixed -> อื่นๆ (asset_purchase_method_11)
        purchase_methods = self.asset_ids.mapped('asset_purchase_method_id')
        new_purchase_method = (len(purchase_methods) == 1 and
                               purchase_methods[0] or
                               self.env.ref('pabi_asset_management.'
                                            'asset_purchase_method_11'))
        # Prepare Old Move
        move_lines = []
        partner_ids = []
        for asset in self.asset_ids:
            if asset.partner_id:
                partner_ids.append(asset.partner_id.id)
            if asset.purchase_value:
                move_lines += [
                    # -------------------- OLD OWNER ----------------------
                    # Cr Asset Value (Old)
                    {
                        'asset_id': False,
                        'account_id':
                        asset.profile_id.account_asset_id.id,
                        'partner_id': asset.partner_id.id,
                        'name': asset.display_name,
                        # Value
                        'credit': (asset.purchase_value > 0.0 and
                                   asset.purchase_value or 0.0),
                        'debit': (asset.purchase_value < 0.0 and
                                  -asset.purchase_value or 0.0),
                        # Budget
                        'project_id': asset.owner_project_id.id,
                        'section_id': asset.owner_section_id.id,
                        'invest_asset_id': asset.owner_invest_asset_id.id,
                        'invest_construction_phase_id':
                        asset.owner_invest_construction_phase_id.id,
                     },
                ]
            if asset.value_depreciated:
                move_lines += [
                    # Dr Accum Depre (Old)
                    {
                        'asset_id': False,
                        'account_id':
                        asset.profile_id.account_depreciation_id.id,
                        'partner_id': asset.partner_id.id,
                        'name': asset.display_name,
                        # Value
                        'credit': (asset.value_depreciated < 0.0 and
                                   -asset.value_depreciated or 0.0),
                        'debit': (asset.value_depreciated > 0.0 and
                                  asset.value_depreciated or 0.0),
                        # Budget
                        'project_id': asset.owner_project_id.id,
                        'section_id': asset.owner_section_id.id,
                        'invest_asset_id': asset.owner_invest_asset_id.id,
                        'invest_construction_phase_id':
                        asset.owner_invest_construction_phase_id.id,
                     },
                ]

        _logger.info("move_lines1: %s", str(move_lines))
        # All source assset must has single partner
        partner_ids = list(set(partner_ids))
        if len(partner_ids) != 1:
            raise ValidationError(
                _('All source asset must belong to single partner.'))
        count = len(self.target_asset_ids)
        total_depre = sum(self.asset_ids.mapped('value_depreciated'))
        accum_depre = 0.0
        i = 0
        for target_asset in self.target_asset_ids:
            i += 1
            # Ratio
            ratio = 1.0
            if self.source_asset_value:
                ratio = (target_asset.depreciation_base /
                         self.source_asset_value)
            # Property of New Asset
            new_product = target_asset.product_id
            new_asset_profile = new_product.asset_profile_id
            # Force to AN before lek think it should be fixed.
            # new_journal = new_asset_profile.journal_id
            new_journal = self.journal_id
            new_account_asset = new_asset_profile.account_asset_id
            # For transfer, for each new asset, update following fields
            if target_asset.depreciation_base:
                new_asset_move_line_dict = {
                    'asset_id': False,
                    'account_id': new_account_asset.id,
                    'partner_id': partner_ids[0],
                    'name': target_asset.asset_name,
                    'product_id': new_product.id,
                    'asset_profile_id': new_asset_profile.id,  # New Asset
                    # Value
                    'credit': (target_asset.depreciation_base < 0.0 and
                               -target_asset.depreciation_base or 0.0),
                    'debit': (target_asset.depreciation_base > 0.0 and
                              target_asset.depreciation_base or 0.0),
                    # Budget
                    'project_id': project.id,
                    'section_id': section.id,
                    'invest_asset_id': invest_asset.id,
                    'invest_construction_phase_id': invest_construction_phase.id,
                }
                move_lines.append(new_asset_move_line_dict)
            # Depreciation Move Line
            if total_depre:
                new_depre = 0.0
                if i == count:
                    new_depre = total_depre - accum_depre
                else:
                    new_depre = ratio * total_depre
                new_depre_dict = {
                    'asset_id': False,
                    'account_id':
                    new_asset_profile.account_depreciation_id.id,
                    'partner_id': partner_ids[0],
                    'name': target_asset.asset_name,
                    # Value
                    'credit': new_depre > 0.0 and new_depre or 0.0,
                    'debit': new_depre < 0.0 and -new_depre or 0.0,
                    # Budget
                    'project_id': project.id,
                    'section_id': section.id,
                    'invest_asset_id': invest_asset.id,
                    'invest_construction_phase_id': invest_construction_phase.id,
                }
                accum_depre += new_depre
                move_lines.append(new_depre_dict)
        _logger.info("move_lines2: %s", str(move_lines))

        # Finalize all moves before create it.
        final_move_lines = [(0, 0, x) for x in move_lines]
        move_dict = {'journal_id': new_journal.id,
                     'line_id': final_move_lines,
                     'period_id': Period.find(self.date).id,
                     'date': self.date,
                     'date_document': fields.Date.context_today(self),
                     'ref': self.name}
        ctx = {'asset_purchase_method_id': new_purchase_method.id,
               'direct_create': True}  # direct_create to recalc dimension
        _logger.info("move_dict: %s", str(move_dict))
        move = AccountMove.with_context(ctx).create(move_dict)
        _logger.info("move: %s", str(move))
        # For transfer, new asset should be created
        new_assets = move.line_id.mapped('asset_id')
        if len(new_assets) != len(self.target_asset_ids):
            raise ValidationError(
                _('%s asset(s) should be created, something went wrong!') %
                len(self.target_asset_ids))
        for asset in new_assets:
            asset.source_asset_ids = self.asset_ids
        self.asset_ids.write({
            'active': False,
            'target_asset_ids': [(4, x) for x in new_assets.ids],
            'status': AssetStatus.search([('code', '=', 'transfer')]).id,
            'state': 'removed',
            'date_remove': self.date,
        })
        for asset in self.asset_ids:
            if asset.profile_type == 'normal':
                self._remove_asset_line(asset)
        self.write({'new_asset_ids': [(4, x) for x in new_assets.ids],
                    'move_id': move.id})

        # copy owner data from source to target asset
        src_asset = self.asset_ids[0]
        src_owner_section_id = src_asset.owner_section_id
        src_owner_project_id = src_asset.owner_project_id
        src_owner_invest_asset_id = src_asset.owner_invest_asset_id
        src_owner_invest_construction_phase_id = \
            src_asset.owner_invest_construction_phase_id
        for new_asset in new_assets:
            new_asset.owner_section_id = src_owner_section_id
            new_asset.owner_project_id = src_owner_project_id
            new_asset.owner_invest_asset_id = src_owner_invest_asset_id
            new_asset.owner_invest_construction_phase_id = \
                src_owner_invest_construction_phase_id

        return True

    @api.multi
    def open_source_asset(self):
        self.ensure_one()
        action = self.env.ref('account_asset_management.account_asset_action')
        result = action.read()[0]
        assets = self.env['account.asset'].with_context(active_test=False).\
            search([('id', 'in', self.asset_ids.ids)])
        dom = [('id', 'in', assets.ids)]
        result.update({'domain': dom, 'context': {'active_test': False}})
        return result

    @api.multi
    def open_target_asset(self):
        self.ensure_one()
        action = self.env.ref('account_asset_management.account_asset_action')
        result = action.read()[0]
        target_assets = self.new_asset_ids
        assets = self.env['account.asset'].with_context(active_test=False).\
            search([('id', 'in', target_assets.ids)])
        dom = [('id', 'in', assets.ids)]
        result.update({'domain': dom, 'context': {'active_test': False}})
        return result

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
            'domain': [('id', '=', self.move_id.id)],
        }


class AccountAssetTransferTarget(models.Model):
    _name = 'account.asset.transfer.target'

    transfer_id = fields.Many2one(
        'account.asset.transfer',
        string='Asset Transfer',
        index=True,
        ondelete='cascade',
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
        size=500,
    )
    asset_profile_id = fields.Many2one(
        'account.asset.profile',
        related='product_id.asset_profile_id',
        string='To Asset Category',
        store=True,
        readonly=True,
    )
    depreciation_base = fields.Float(
        string='Value',
        required=True,
        default=0.0,
    )
    # ref_asset_id = fields.Many2one(
    #     'account.asset',
    #     string='New Asset',
    #     readonly=True,
    #     ondelete='restrict',
    # )
    # move_id = fields.Many2one(
    #     'account.move',
    #     string='Journal Entry',
    #     readonly=True,
    #     copy=False,
    # )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.asset_name = self.product_id.name

    @api.multi
    @api.constrains('depreciation_base')
    def _check_asset_value(self):
        for rec in self:
            if float_compare(rec.depreciation_base, 0.0, 2) == -1:
                raise ValidationError(_('Negative asset value not allowed!'))
