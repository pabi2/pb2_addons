# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError, ValidationError


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
    compute_method = fields.Selection(
        [('standard', 'Standard - 1 JE per Asset'),
         ('standard_fast', 'Standard - 1 JE per Asset (Fast Logic)'),
         ('grouping', 'Grouping - 1 JE per Asset Profile'), ],
        string='Compute Method',
        default='standard_fast',
        required=True,
        help="Method of generating depreciation journal entries\n"
        "* Standard: create 1 JE for each asset depreciation line\n"
        "* Grouping: create 1 JE by grouping depreciation with same "
        "asset profile",
    )
    grouping_date = fields.Date(
        string='Date',
        default=lambda self: fields.Date.context_today(self),
        help="For Grouping method, this date will be used to create JE",
    )
    categ_ids = fields.Many2many(
        'product.category',
        'pabi_action_asset_compute_product_category_rel',
        'compute_id', 'category_id',
        string='Category',
        domain=lambda self: self._get_categ_domain()
    )
    profile_ids = fields.Many2many(
        'account.asset.profile',
        'pabi_action_asset_compute_account_asset_profile_rel',
        'compute_id', 'profile_id',
        string='Profile',
        domain=[('no_depreciation', '=', False)],
    )
    test_log_ids = fields.One2many(
        'pabi.action.asset.compute.test.log',
        'wizard_id',
        string='Asset Test Log',
        readonly=True,
    )
    run_state = fields.Selection(
        [('run', 'Run Asset'),
         ('test', 'Test Result')],
        string='Run State',
        default='run',
    )
    batch_note = fields.Char(
        string='Batch Note',
        size=500,
        help="Note that will be filled in asset depreciation batch",
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
        asset_ids = self._search_asset(self.calendar_period_id,
                                       self.categ_ids.ids,
                                       self.profile_ids.ids)
        # Assume 1 depre line for 1 asset always
        raise UserError(
            _('%s assets will be computed in this operation') % len(asset_ids))

    @api.model
    def _get_categ_domain(self):
        asset_journal = self.env.ref('pabi_asset_management.journal_asset')
        return [('property_stock_journal', '=', asset_journal.id),
                ('type', '=', 'normal')]

    @api.model
    def _search_asset(self, period, categ_ids, profile_ids,
                      return_as_groups=False):
        # SQL to find asset_ids based on search criteria
        from_sql = """
            from account_asset a
            join account_asset_profile p on a.profile_id = p.id
            join product_category c on c.id = p.product_categ_id
            where 1 = 1 and p.no_depreciation = false
            %s -- profile_cond
            %s -- categ_cond
        """
        p, c = '', ''
        if profile_ids:
            profiles = str(profile_ids).replace('[', '(').replace(']', ')')
            p = 'and p.id in %s' % profiles
        if categ_ids:
            categs = str(categ_ids).replace('[', '(').replace(']', ')')
            c = 'and c.id in %s' % categs
        from_str = from_sql % (p, c)
        # With group by
        groups = []
        if return_as_groups:
            # Compute method grouping, find the group by criterias
            # By doing this, 1 JE will be created for each asset profile
            GROUPBY = ['profile_id']
            # GROUPBY = ['account_depreciation_id',
            #            'account_expense_depreciation_id',
            #            'owner_section_id',
            #            'owner_project_id',
            #            'owner_invest_asset_id',
            #            'owner_invest_construction_phase_id', ]
            fields_str = ', '.join(GROUPBY)
            self._cr.execute("select distinct %s %s" %
                             (fields_str, from_str))
            groups = self._cr.dictfetchall()  # i.e., [{'x': 1, 'y': 2}, {}]
        else:
            # Compute method standard, 1 group only
            groups = [{1: 1}]  # and 1=1, which is no harm

        group_assets = {}  # Return as {'Group1': [1,2,3,4], ...}
        for g in groups:
            # Formulate where clause
            wheres = []
            for key, val in g.iteritems():
                if val:
                    wheres.append('%s = %s' % (key, val))
                else:
                    wheres.append('%s is null' % key)
            where_str = ' and '.join(wheres)
            # Select assets based on search criteria
            self._cr.execute("select distinct a.id %s and %s" %
                             (from_str, where_str))
            asset_ids = [x[0] for x in self._cr.fetchall()] or [0]
            # Find valid depreciation line, based on asset_ids
            self._cr.execute("""
                select a.id
                from account_asset_line al
                    join account_asset a on a.id = al.asset_id
                where a.state = 'open' and a.type = 'normal'
                    and a.active = true and al.type = 'depreciate'
                    and al.init_entry = false and al.move_check = false
                    and exists (select 1 from account_asset where a.id in %s)
                    and al.line_date between %s and %s
            """, (tuple(asset_ids), period.date_start, period.date_stop))
            asset_ids = [x[0] for x in self._cr.fetchall()]
            if asset_ids:
                group_assets.update({str(g): asset_ids})

        if return_as_groups:  # {group: asset_ids, ...}
            return group_assets or {}
        else:  # asset_ids
            return group_assets and group_assets.values()[0] or []

    @api.multi
    def asset_compute(self, period_id, categ_ids, profile_ids,
                      batch_note, compute_method='standard_fast',
                      grouping_date=False):
        period = self.env['account.period'].browse(period_id)
        # Block future period
        # current_period = self.env['account.period'].find()
        # Future period allow?
        # if not self._context.get('allow_future_period', False) and \
        #         period.date_start > current_period.date_start:
        #     raise ValidationError(_('Compute asset depreciation for '
        #                             'future period is not allowed!'))
        # Batch ID
        depre_batch = self.env['pabi.asset.depre.batch'].new_batch(period,
                                                                   batch_note)

        group_assets = {}  # Group of assets from search
        created_move_ids = []
        error_logs = []
        fast_create_move = compute_method == 'standard_fast'
        if compute_method == 'grouping':  # Groupby Account, Depre Budget
            group_assets = self._search_asset(period, categ_ids, profile_ids,
                                              return_as_groups=True)
        else:  # standard
            asset_ids = self._search_asset(period, categ_ids, profile_ids)
            if asset_ids:
                group_assets['N/A'] = asset_ids
        if not group_assets:
            raise ValidationError(
                _('No more assets to compute for this period!'))
        # Compute for each group (1 group for standard case)
        for grp_name, asset_ids in group_assets.iteritems():
            self = self.with_context(batch_id=depre_batch.id)
            assets = self.env['account.asset'].browse(asset_ids)
            merge_move = (compute_method == 'grouping') and True or False
            move_ids, error_log = assets._compute_entries(
                period, check_triggers=True,
                merge_move=merge_move, merge_date=grouping_date,
                fast_create_move=fast_create_move)
            created_move_ids += move_ids
            if error_log and error_log != '':
                error_logs.append(error_log)
        # Return
        result_msg = '\n'.join(error_logs)
        if not result_msg:
            result_msg = _('Computed depreciation created %s '
                           'journal entries') % len(created_move_ids)
        return (depre_batch, result_msg)

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
                  'profile_ids': self.profile_ids.ids,
                  'batch_note': self.batch_note,
                  'compute_method': self.compute_method,
                  'grouping_date': self.grouping_date,
                  }
        #check state draft in pabi_asset_depre_batch
        check_state_draft = self.env['pabi.asset.depre.batch'].search([('state', '=', 'draft')]) 
        if (check_state_draft!=Null):
             raise UserError(
            _('Have states draft in pabi_asset_depre_batch ') ) 
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
        #check state draft in pabi_asset_depre_batch
        check_state_draft = self.env['pabi.asset.depre.batch'].search([('state', '=', 'draft')]) 
        if (check_state_draft!=Null):
             raise UserError(
            _('Have states draft in pabi_asset_depre_batch ') )
             
        self.ensure_one()             
        self.test_log_ids.unlink()
        asset_ids = self._search_asset(
            self.calendar_period_id, self.categ_ids.ids,
            self.profile_ids.ids
        )
        # TEST
        assets = self.env['account.asset'].browse(asset_ids)
        self._log_test_period_closed(self.calendar_period_id)
        self._log_test_asset_profile_account(assets)
        self._log_test_prev_depre_posted(self.calendar_period_id, assets)
        self._log_test_active_chartfield(assets)
        self.write({'run_state': 'test'})
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
            # Test with ower chartfield (for depre)
            self._cr.execute("""
                select id asset_id,
                    owner_section_id as section_id,
                    owner_project_id as project_id,
                    owner_invest_asset_id as invest_asset_id,
                    owner_invest_construction_phase_id
                        as invest_construction_phase_id
                from account_asset
                where id in %s and
                (
                 owner_section_id in (select res_id from chartfield_view
                    where model = 'res.section' and active = false) or
                 owner_project_id in (select res_id from chartfield_view
                    where model = 'res.project' and active = false) or
                 owner_invest_asset_id in (select res_id from chartfield_view
                    where model = 'res.invest.asset' and active = false) or
                 owner_invest_construction_phase_id in (select res_id from
                    chartfield_view where model =
                    'res.invest.construction.phase' and active = false)
                )
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
                message = _("Inactive asset profile's account code: %s") % \
                    account.code
                logs.append((0, 0, {'message': message}))
            self.write({'test_log_ids': logs})
        return True

    @api.multi
    def _log_test_prev_depre_posted(self, period, assets):
        self.ensure_one()
        Asset = self.env['account.asset']
        if assets:
            logs = []
            unposted_asset_ids = assets._test_prev_depre_unposted(period)
            assets = Asset.browse(unposted_asset_ids)
            for asset in assets:
                message = \
                    _("Unposted lines prior to period: %s")
                logs.append((0, 0, {'asset_id': asset.id,
                                    'message': message % period.name}))
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
        size=1000,
    )
