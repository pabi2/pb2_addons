# -*- coding: utf-8 -*-
import ast
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class PabiActionAssetCompute(models.TransientModel):
    """ PABI Action for Compute Asset Depreciation """
    _name = 'pabi.action.asset.compute'
    _inherit = 'pabi.action'

    # Criteria
    calendar_period_id = fields.Many2one(
        'account.period.calendar',
        string='Period',
        domain=[('state', '=', 'draft')],
        default=lambda self: self.env['account.period'].find().id,
        required=True,
    )
    categ_ids = fields.Many2many(
        'product.category',
        string='Category',
        domain=lambda self: self._get_categ_domain()
    )
    profile_ids = fields.Many2many(
        'account.asset.profile',
        string='Profile',
    )
    test_log_ids = fields.One2many(
        'pabi.action.asset.compute.test.log',
        'wizard_id',
        string='Asset Test Log',
        readonly=True,
    )
    test_completed = fields.Boolean(
        string='Test Completed',
        default=False,
    )
    max_asset_test = fields.Integer(
        string='Max Assets',
        default=1000,
    )
    run_state = fields.Selection(
        [('run', 'Run Asset'),
         ('test', 'Test Result')],
        string='Run State',
        default='run',
    )
    tested_assets = fields.Char(  # unlimited size
        string='Tested Assets',
        default='[]',
        help="String representative of tested asset_ids, i.e, '[1,2,4]'"
    )

    @api.onchange('calendar_period_id')
    def _onchange_calendar_period_id(self):
        self.categ_ids = False
        self.profile_ids = False
        self.test_assets = '[]'

    @api.onchange('categ_ids')
    def _onchange_categ_ids(self):
        self.profile_ids = False
        self.test_assets = '[]'

    @api.onchange('profile_ids')
    def _onchange_profile_ids(self):
        self.test_assets = '[]'

    @api.multi
    def check_affected_asset(self):
        self.ensure_one()
        assets = self._search_asset(self.calendar_period_id,
                                    self.categ_ids.ids,
                                    self.profile_ids.ids)
        # Assume 1 depre line for 1 asset always
        num_asset = len(assets)
        raise UserError(
            _('%s assets will be computed in this operation') % num_asset)

    @api.model
    def _get_categ_domain(self):
        asset_journal = self.env.ref('pabi_asset_management.journal_asset')
        return [('property_stock_journal', '=', asset_journal.id),
                ('type', '=', 'normal')]

    @api.model
    def _search_asset(self, period, categ_ids, profile_ids,
                      exclude_asset_ids=[], limit=False):
        # Serach for matched asset depre lines first
        domain = [
            ('asset_id.state', '=', 'open'),
            ('asset_id.type', '=', 'normal'),
            ('type', '=', 'depreciate'),
            ('init_entry', '=', False),
            ('line_date', '<=', period.date_stop),
            ('line_date', '>=', period.date_start),
            ('move_check', '=', False)
        ]
        if categ_ids:
            domain += [('asset_id.profile_id.product_categ_id',
                        'in', categ_ids)]
        if profile_ids:
            domain += [('asset_id.profile_id', 'in', profile_ids)]
        if exclude_asset_ids:
            domain += [('asset_id', 'not in', exclude_asset_ids)]
        depre_lines = self.env['account.asset.line'].search(domain)
        # Find Assets
        domain = [('depreciation_line_ids', 'in', depre_lines.ids)]
        assets = self.env['account.asset'].search(domain, limit=limit)
        return assets

    @api.multi
    def asset_compute(self, period_id, categ_ids, profile_ids):
        period = self.env['account.period'].browse(period_id)
        assets = self._search_asset(period, categ_ids, profile_ids)
        created_move_ids, error_log = \
            assets._compute_entries(period, check_triggers=True)
        # Return
        records = self.env['account.move'].browse(created_move_ids)
        if not error_log:
            error_log = _('Computed depreciation for %s assets') % len(records)
        result_msg = error_log
        return (records, result_msg)

    @api.multi
    def pabi_action(self):
        self.ensure_one()
        # Prepare job information
        process_xml_id = 'pabi_async_process.asset_compute'
        job_desc = _('Compute Asset Depreciation for %s by %s' %
                     (self.calendar_period_id.display_name,
                      self.env.user.display_name))
        func_name = 'asset_compute'
        # Prepare kwargs, the params for method action_generate
        kwargs = {'period_id': self.calendar_period_id.id,
                  'categ_ids': self.categ_ids.ids,
                  'profile_ids': self.profile_ids.ids, }
        # Call the function
        res = super(PabiActionAssetCompute, self).\
            pabi_action(process_xml_id, job_desc, func_name, **kwargs)
        return res

    @api.multi
    def action_back(self):
        self.ensure_one()
        self.write({'run_state': 'run'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pabi.action.asset.compute',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.multi
    def run_asset_test(self):
        """ Based on matched assets, run through series of test """
        self.ensure_one()
        # Matched assets exclude tested one
        tested_asset_ids = ast.literal_eval(self.tested_assets)
        assets = self._search_asset(
            self.calendar_period_id, self.categ_ids.ids,
            self.profile_ids.ids, exclude_asset_ids=tested_asset_ids,
            limit=self.max_asset_test
        )
        tested_asset_ids += assets.ids
        # TEST
        self._log_test_period_closed(self.calendar_period_id)
        self._log_test_asset_profile_account(assets)
        self._log_test_prev_depre_posted(self.calendar_period_id, assets)
        self._log_test_active_chartfield(assets)
        self.write({'run_state': 'test',
                    'tested_assets': str(tested_asset_ids),
                    'test_completed': not assets.ids and True or False,
                    })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pabi.action.asset.compute',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.model
    def _log_test_period_closed(self, period):
        if period.state == 'done':
            message = _('Period %s is closed') % period.calendar_name
            self.write({'test_log_ids': [(0, 0, {'message': message})]})
        return True

    @api.model
    def _log_test_active_chartfield(self, assets):
        if assets:
            Analytic = self.env['account.analytic.account']
            logs = []
            self._cr.execute("""
                select id asset_id, section_id, project_id, invest_asset_id,
                    invest_construction_phase_id, costcenter_id
                from account_asset
                where id in %s
            """, (tuple(assets.ids), ))
            results = self._cr.dictfetchall()
            for res in results:
                active, err_message = Analytic.test_chartfield_active(res)
                if not active:
                    logs.append((0, 0, {'asset_id': res['asset_id'],
                                        'message': err_message}))
            self.write({'test_log_ids': logs})
        return True

    @api.model
    def _log_test_asset_profile_account(self, assets):
        """ Test whether any of account from asset profile is inactive """
        if assets:
            logs = []
            self._cr.execute("""
                select id as account_id from account_account
                where active = false
                and id in (
                select distinct account_depreciation_id account_id
                from account_asset_profile
                where account_depreciation_id is not null and id in
                (select distinct profile_id from account_asset where id in %s)
                union
                select distinct account_expense_depreciation_id account_id
                from account_asset_profile
                where account_expense_depreciation_id is not null and id in
                (select distinct profile_id from account_asset where id in %s))
            """, (tuple(assets.ids), tuple(assets.ids)))
            account_ids = [x[0] for x in self._cr.fetchall()]
            accounts = self.env['account.account'].browse(account_ids)
            for account in accounts:
                message = _("Profile's account code, %s, is inactive") % \
                    account.code
                logs.append((0, 0, {'message': message}))
            self.write({'test_log_ids': logs})
        return True

    @api.multi
    def _log_test_prev_depre_posted(self, period, assets):
        self.ensure_one()
        Asset = self.env['account.asset']
        logs = []
        for asset in assets:
            posted, err_message = Asset._test_prev_depre_posted(period, asset)
            if not posted:
                logs.append((0, 0, {'asset_id': asset.id,
                                    'message': err_message}))
        self.write({'test_log_ids': logs})
        return True


class PabiActionAssetComputeTestLog(models.TransientModel):
    _name = 'pabi.action.asset.compute.test.log'
    _order = 'id desc'

    wizard_id = fields.Many2one(
        'pabi.action.asset.compute',
        string='Wizard ID',
        ondelete='cascade',
        readonly=True,
    )
    asset_id = fields.Many2one(
        'account.asset',
        string='Asset',
        readonly=True,
    )
    message = fields.Char(
        string='Message',
        readonly=True,
    )
