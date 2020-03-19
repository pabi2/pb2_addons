# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.exceptions import Warning as UserError
from openerp.exceptions import RedirectWarning
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import RetryableJobError

@job
def action_done_async_process(session, model_name, res_id):
    try:
        res = session.pool[model_name].action_done_background(
            session.cr, session.uid, [res_id], session.context)
        return {'result': res}
    except Exception, e:
        raise RetryableJobError(e)


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
        'account.asset.removal.lines',
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
        related='target_status.code'
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
    queue_job_id = fields.Many2one(
        'queue.job',
        string='Queue Job',
        store=True,
    )
    queue_job_uuid = fields.Char(
        string='Queue Job UUID',
        store=True,
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
        for removal in self:
            asset_ids = removal.removal_asset_ids.mapped('asset_id').ids
            assets_id = Asset.with_context(active_test=False).search([
                ('id', 'in', asset_ids)])

            for asset in assets_id:
                res = asset.open_entries()
                move_id = self.env['account.move'].search(res['domain'])
                for move in move_id:
                    if move.state == 'draft':
                        move.line_id._get_detail_asset_move_line()
                        move.button_validate()

    @api.multi
    def _remove_confirmed_assets(self):
        for removal in self:
            if not removal.removal_asset_ids:
                raise ValidationError(_('No asset to remove!'))
            for line in removal.removal_asset_ids:
                if line.asset_id.state not in ('open', 'close'):
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
    def action_done_background(self):
        self.ensure_one()
        if self._context.get('job_uuid', False):  # Called from @job
            return self.action_done()
        if self.queue_job_id:
            message = ('Remove Asset')
            action = self.env.ref('pabi_utils.action_my_queue_job')
            raise RedirectWarning(message, action.id, ('Go to My Jobs'))
        session = ConnectorSession(self._cr, self._uid, self._context)
        description = '%s - Commitment Asset Removal' % (self.name)
        uuid = action_done_async_process.delay(
            session, self._name, self.id, description=description)
        job = self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
        self.queue_job_id = job.id
        self.queue_job_uuid = uuid

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
        dom = [
            ('id', 'in', assets.ids),
            ('active', '=', False)
        ]
        result.update({'domain': dom})
        return result


class AccountAssetRemovalLines(models.Model):
    _name = 'account.asset.removal.lines'

    _sql_constraints = [
        ('asset_id_unique', 'unique(asset_id, removal_id)', 'Duplicate assets selected!'),
        ('sale_value', 'CHECK (sale_value>=0)', 'The Sale Value must be positive!')]

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
                ('state', 'in', ('open', 'close'))],
        required=True,
        ondelete='restrict',
    )
    target_status = fields.Many2one(
        'account.asset.status',
        string='Asset Status',
        domain="[('map_state_removed', '=', 'removed')]",
        required=True,
    )
    date_remove = fields.Date(
        string='Asset Removal Date',
        default=fields.Date.today,
        required=True,
    )
    period_id = fields.Many2one(
        comodel_name='account.period',
        string='Force Period',
        domain=[('state', '!=', 'done'), ('special', '=', False)],
    )
    sale_value = fields.Float(
        string='Sale Value',
        default=lambda self: self._default_sale_value(),
    )
    account_sale_id = fields.Many2one(
        comodel_name='account.account',
        string='Asset Sale Account',
        domain=[('type', '=', 'other')],
        default=lambda self: self._default_account_sale_id(),
    )
    account_plus_value_id = fields.Many2one(
        comodel_name='account.account',
        string='Plus-Value Account',
        domain=[('type', '=', 'other')],
        # default=lambda self: self._default_account_plus_value_id()
    )
    account_min_value_id = fields.Many2one(
        comodel_name='account.account',
        string='Min-Value Account',
        domain=[('type', '=', 'other')],
        # default=lambda self: self._default_account_min_value_id()
    )
    account_residual_value_id = fields.Many2one(
        comodel_name='account.account',
        string='Residual Value Account',
        domain=[('type', '=', 'other')],
        # default=lambda self: self._default_account_residual_value_id()
    )
    posting_regime = fields.Selection(
        selection=lambda self: self._selection_posting_regime(),
        string='Removal Entry Policy',
        required=True,
        default=lambda self: self._get_posting_regime(),
    )
    note = fields.Text('Notes')

    @api.model
    def _default_sale_value(self):
        return self._get_sale()['sale_value']

    @api.model
    def _default_account_sale_id(self):
        return self._get_sale()['account_sale_id']

    def _get_sale(self):
        asset_id = self._context.get('active_id')
        sale_value = 0.0
        account_sale_id = False
        inv_lines = self.env['account.invoice.line'].search(
            [('asset_id', '=', asset_id or 0)])
        for line in inv_lines:
            inv = line.invoice_id
            comp_curr = inv.company_id.currency_id
            inv_curr = inv.currency_id
            if line.invoice_id.state in ['open', 'paid']:
                account_sale_id = line.account_id.id
                amount = line.price_subtotal
                if inv_curr != comp_curr:
                    amount = comp_curr.compute(amount, inv_curr)
                sale_value += amount
        return {'sale_value': sale_value, 'account_sale_id': account_sale_id}

    @api.model
    def _default_account_plus_value_id(self):
        asset_id = self._context.get('active_id')
        asset = self.env['account.asset'].browse(asset_id)
        return asset.profile_id.account_plus_value_id

    @api.model
    def _default_account_min_value_id(self):
        asset_id = self._context.get('active_id')
        asset = self.env['account.asset'].browse(asset_id)
        return asset.profile_id.account_min_value_id

    @api.model
    def _default_account_residual_value_id(self):
        asset_id = self._context.get('active_id')
        asset = self.env['account.asset'].browse(asset_id)
        return asset.profile_id.account_residual_value_id

    @api.model
    def _selection_posting_regime(self):
        return[
            ('residual_value', _('Residual Value')),
            ('gain_loss_on_sale', _('Gain/Loss on Sale')),
        ]

    @api.model
    def _get_posting_regime(self):
        # asset_obj = self.env['account.asset']
        # asset = asset_obj.browse(self._context.get('active_id'))
        if self.asset_id:
            country = self.asset_id.company_id.country_id.code or False
            if country in self._residual_value_regime_countries():
                return 'residual_value'
            elif self.target_status.code == 'deliver':
                return 'residual_value'
            else:
                return 'gain_loss_on_sale'
        elif self.removal_id.target_status and \
                self.removal_id.target_status.code == 'deliver':
            return 'residual_value'
        else:
            return 'gain_loss_on_sale'

    def _residual_value_regime_countries(self):
        return ['FR']

    @api.multi
    def remove(self):
        self.ensure_one()
        asset_obj = self.env['account.asset']
        asset_line_obj = self.env['account.asset.line']
        move_obj = self.env['account.move']

        asset_id = self._context.get('active_id')
        asset = asset_obj.browse(asset_id)
        asset_ref = asset.code and '%s (ref: %s)' \
            % (asset.name, asset.code) or asset.name

        if self._context.get('early_removal'):
            residual_value = self._prepare_early_removal(asset)
        else:
            residual_value = asset.value_residual
        ctx = dict(self._context, company_id=asset.company_id.id)
        period_id = self.period_id.id
        if not period_id:
            ctx.update(account_period_prefer_normal=True)
            period_ids = self.env['account.period'].with_context(ctx).find(
                self.date_remove)
            if not period_ids:
                raise UserError(_(
                    "No period defined for the removal date."))
            period_id = period_ids[0].id
        dlines = asset_line_obj.search(
            [('asset_id', '=', asset.id), ('type', '=', 'depreciate')],
            order='line_date desc')
        if dlines:
            last_date = dlines[0].line_date
        else:
            create_dl = asset_line_obj.search(
                [('asset_id', '=', asset.id), ('type', '=', 'create')])[0]
            last_date = create_dl.line_date
        if self.date_remove < last_date:
            raise UserError(
                _("The removal date must be after "
                  "the last depreciation date."))

        line_name = asset._get_depreciation_entry_name(len(dlines) + 1)
        journal_id = asset.profile_id.journal_id.id
        # create move
        move_vals = {
            'name': asset.name,
            'date': self.date_remove,
            'ref': line_name,
            'period_id': period_id,
            'journal_id': journal_id,
            'narration': self.note,
        }
        move = move_obj.create(move_vals)
        # create asset line
        asset_line_vals = {
            'amount': residual_value,
            'asset_id': asset_id,
            'name': line_name,
            'line_date': self.date_remove,
            'move_id': move.id,
            'type': 'remove',
        }
        asset_line_obj.create(asset_line_vals)
        asset.write({
            'state': 'removed',
            'date_remove': self.date_remove,
            'active': False,
        })

        # create move lines
        move_lines = self._get_removal_data(asset, residual_value)
        move.with_context(allow_asset=True).write({'line_id': move_lines})

        return {
            'name': _("Asset '%s' Removal Journal Entry") % asset_ref,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': self._context,
            'nodestroy': True,
            'domain': [('id', '=', move.id)],
        }

    def _prepare_early_removal(self, asset):
        # Generate last depreciation entry on the day before the removal date.

        date_remove = self.date_remove
        asset_line_obj = self.env['account.asset.line']

        digits = self.env['decimal.precision'].precision_get('Account')

        def _dlines(asset):
            lines = asset.depreciation_line_ids
            dlines = lines.filtered(
                lambda l: l.type == 'depreciate' and not
                l.init_entry and not l.move_check)
            dlines = dlines.sorted(key=lambda l: l.line_date)
            return dlines

        dlines = _dlines(asset)
        if not dlines:
            asset.compute_depreciation_board()
            dlines = _dlines(asset)
        first_to_depreciate_dl = dlines[0]

        first_date = first_to_depreciate_dl.line_date
        if date_remove > first_date:
            raise UserError(
                _("You can't make an early removal if all the depreciation "
                  "lines for previous periods are not posted."))

        if first_to_depreciate_dl.previous_id:
            last_depr_date = first_to_depreciate_dl.previous_id.line_date
        else:
            create_dl = asset_line_obj.search(
                [('asset_id', '=', asset.id), ('type', '=', 'create')])
            last_depr_date = create_dl.line_date

        period_number_days = (
            datetime.strptime(first_date, '%Y-%m-%d') -
            datetime.strptime(last_depr_date, '%Y-%m-%d')).days
        date_remove = datetime.strptime(date_remove, '%Y-%m-%d')
        new_line_date = date_remove + relativedelta(days=-1)
        to_depreciate_days = (
            new_line_date -
            datetime.strptime(last_depr_date, '%Y-%m-%d')).days
        to_depreciate_amount = round(
            float(to_depreciate_days) / float(period_number_days) *
            first_to_depreciate_dl.amount, digits)
        residual_value = asset.value_residual - to_depreciate_amount
        if to_depreciate_amount:
            update_vals = {
                'amount': to_depreciate_amount,
                'line_date': new_line_date
            }
            first_to_depreciate_dl.write(update_vals)
            dlines[0].create_move()
            dlines -= dlines[0]
        dlines.unlink()
        return residual_value

    def _get_removal_data(self, asset, residual_value):
        move_lines = []
        partner_id = asset.partner_id and asset.partner_id.id or False
        profile = asset.profile_id

        # asset and asset depreciation account reversal
        depr_amount = asset.depreciation_base - residual_value
        if depr_amount:
            move_line_vals = {
                'name': asset.name,
                'account_id': profile.account_depreciation_id.id,
                'debit': depr_amount > 0 and depr_amount or 0.0,
                'credit': depr_amount < 0 and -depr_amount or 0.0,
                'partner_id': partner_id,
                'asset_id': asset.id
            }
            move_lines.append((0, 0, move_line_vals))
        move_line_vals = {
            'name': asset.name,
            'account_id': profile.account_asset_id.id,
            'debit': asset.purchase_value < 0 and -asset.purchase_value or 0.0,
            'credit': asset.purchase_value > 0 and asset.purchase_value or 0.0,
            'partner_id': partner_id,
            'asset_id': asset.id
        }
        move_lines.append((0, 0, move_line_vals))

        if residual_value:
            if self.posting_regime == 'residual_value':
                move_line_vals = {
                    'name': asset.name,
                    'account_id': self.account_residual_value_id.id,
                    'analytic_account_id': asset.account_analytic_id.id,
                    'debit': residual_value + asset.salvage_value,
                    'credit': 0.0,
                    'partner_id': partner_id,
                    'asset_id': asset.id
                }
                move_lines.append((0, 0, move_line_vals))
            elif self.posting_regime == 'gain_loss_on_sale':
                if self.sale_value:
                    sale_value = self.sale_value
                    move_line_vals = {
                        'name': asset.name,
                        'account_id': self.account_sale_id.id,
                        'analytic_account_id': asset.account_analytic_id.id,
                        'debit': sale_value,
                        'credit': 0.0,
                        'partner_id': partner_id,
                        'asset_id': asset.id
                    }
                    move_lines.append((0, 0, move_line_vals))
                balance = \
                    self.sale_value - residual_value - asset.salvage_value
                account_id = (self.account_plus_value_id.id
                              if balance > 0
                              else self.account_min_value_id.id)
                move_line_vals = {
                    'name': asset.name,
                    'account_id': account_id,
                    'analytic_account_id': asset.account_analytic_id.id,
                    'debit': balance < 0 and -balance or 0.0,
                    'credit': balance > 0 and balance or 0.0,
                    'partner_id': partner_id,
                    'asset_id': asset.id
                }
                move_lines.append((0, 0, move_line_vals))
        return move_lines

    @api.onchange('asset_id')
    def _onchange_asset_id(self):
        Remove = self.env['account.asset.remove'].\
            with_context(active_id=self.asset_id.id)
        if self.asset_id:
            vals = Remove._get_sale()
            self.sale_value = vals['sale_value']
            self.account_sale_id = vals['account_sale_id']
            if self.posting_regime == 'gain_loss_on_sale':
                self.account_plus_value_id = Remove._default_account_plus_value_id()
                self.account_min_value_id = Remove._default_account_min_value_id()
                self.account_residual_value_id = False
            if self.posting_regime == 'residual_value':
                self.account_residual_value_id = Remove._default_account_residual_value_id()
                self.account_plus_value_id = False
                self.account_min_value_id = False
        else:
            self.posting_regime = self._get_posting_regime()
            self.account_plus_value_id = False
            self.account_min_value_id = False

        if self.posting_regime == 'residual_value' and not (self.account_residual_value_id):
            self.account_residual_value_id = self.env['account.account'].search([('code','=','5206060002')])

    @api.onchange('posting_regime')
    def _onchange_posting_regime(self):
        if self.asset_id:
            Remove = self.env['account.asset.remove'].with_context(active_id=self.asset_id.id)

            if self.posting_regime == 'gain_loss_on_sale':
                self.account_plus_value_id = Remove._default_account_plus_value_id()
                self.account_min_value_id = Remove._default_account_min_value_id()
                self.account_residual_value_id = False
            if self.posting_regime == 'residual_value':
                self.account_residual_value_id = Remove._default_account_residual_value_id()
                self.account_plus_value_id = False
                self.account_min_value_id = False
        else:
            if self.posting_regime == 'residual_value' and not (self.account_residual_value_id):
                self.account_residual_value_id = self.env['account.account'].search([('code','=','5206060002')])
                self.account_plus_value_id = False
                self.account_min_value_id = False
            if self.posting_regime == 'gain_loss_on_sale':
                self.account_residual_value_id = False
