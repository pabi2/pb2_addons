# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountBudget(models.Model):
    _inherit = 'account.budget'

    BUDGET_LEVEL = {
        # Code not cover Activity level yet
        # 'activity_group_id': 'Activity Group',
        # 'activity_id': 'Activity',
        # Fund
        # 'fund_id': 'Fund (for all)',
        'company_id': 'NSTDA',
        # Project Based
        'spa_id': 'SPA',
        'mission_id': 'Mission',
        'functional_area_id': 'Functional Area',
        'program_group_id': 'Program Group',
        'program_id': 'Program',
        'project_group_id': 'Project Group',
        'project_id': 'Project',
        # Unit Based
        'org_id': 'Org',
        'sector_id': 'Sector',
        'subsector_id': 'Subsector',
        'division_id': 'Division',
        'section_id': 'Section',
        'costcenter_id': 'Costcenter',
        # Personnel
        'personnel_costcenter_id': 'Personnel Budget',
        # Investment
        # - Asset
        # 'invest_asset_categ_id': 'Invest. Asset Category',  # (not dimension)
        'invest_asset_id': 'Invest. Asset',
        # - Construction
        'invest_construction_id': 'Construction',
        'invest_construction_phase_id': 'Construction Phase',
    }

    BUDGET_LEVEL_MODEL = {
        # Code not cover Activity level yet
        # 'activity_group_id': 'account.activity.group',
        # 'activity_id': 'Activity'  # No Activity Level{
        # 'fund_id': 'res.fund',
        'spa_id': 'res.spa',
        'mission_id': 'res.mission',
        'tag_type_id': 'res.tag.type',
        'tag_id': 'res.tag',
        # Project Based
        'functional_area_id': 'res.functional.area',
        'program_group_id': 'res.program.group',
        'program_id': 'res.program',
        'project_group_id': 'res.project.group',
        'project_id': 'res.project',
        # Unit Based
        'org_id': 'res.org',
        'sector_id': 'res.sector',
        'subsector_id': 'res.subsector',
        'division_id': 'res.division',
        'section_id': 'res.section',
        'costcenter_id': 'res.costcenter',
        # Personnel
        'personnel_costcenter_id': 'res.personnel.costcenter',
        # Investment
        # - Asset
        # 'invest_asset_categ_id': 'res.invest.asset.category',
        'invest_asset_id': 'res.invest.asset',
        # - Construction
        'invest_construction_id': 'res.invest.construction',
        'invest_construction_phase_id': 'res.invest.construction.phase',
    }

    BUDGET_LEVEL_TYPE = {
        'project_base': 'Project Based',
        'unit_base': 'Unit Based',
        'personnel': 'Personnel',
        'invest_asset': 'Investment Asset',
        'invest_construction': 'Investment Construction',
    }

    budget_release = fields.Selection(
        selection_add=[('auto_rolling', 'Auto Release as Rolling')],
    )

    @api.multi
    def _validate_budget_level(self, budget_type='check_budget'):
        for rec in self:
            budget_type = rec.chart_view
            super(AccountBudget, rec)._validate_budget_level(budget_type)

    # DO NOT REMOVE, we remove this because we don't want to use fund_id level
    # @api.model
    # def _get_budget_monitor(self, fiscal, budget_type,
    #                         budget_level, resource,
    #                         ext_field=False,
    #                         ext_res_id=False,
    #                         blevel=False):
    #     # For funding level, we go deeper, ext is required.
    #     if budget_level == 'fund_id':
    #         budget_type_dict = {
    #             'unit_base': 'monitor_section_ids',
    #             'project_base': 'monitor_project_ids',
    #             'personnel': 'monitor_personnel_costcenter_ids',
    #             'invest_asset': 'monitor_invest_asset_ids',
    #             'invest_construction':
    #             'monitor_invest_construction_phase_ids'
    #         }
    #         return resource[budget_type_dict[budget_type]].\
    #             filtered(lambda x:
    #                      (x.fiscalyear_id == fiscal and
    #                       x[ext_field].id == ext_res_id))
    #     else:
    #         return super(AccountBudget, self).\
    #             _get_budget_monitor(fiscal, budget_type,
    #                                 budget_level, resource)

    @api.model
    def pre_commit_budget_check(self, doc_date, doc_lines,
                                amount_field, doc_currency=False):
        """ Use this to check budget BEFORE commitment """
        currency_id = False
        if doc_currency:
            Currency = self.env['res.currency']
            currency = Currency.search([('name', '=', doc_currency)])
            currency_id = currency and currency[0].id or False
        if doc_currency and not currency_id:
            return {'budget_ok': False,
                    'message': _('Not valid currency on budget check')}
        return self.with_context(currency_id=currency_id).\
            document_check_budget(doc_date, doc_lines,
                                  amount_field=amount_field)

    @api.model
    def post_commit_budget_check(self, doc_date, doc_lines):
        """ Use this to check budget AFTER commitment """
        return self.document_check_budget(doc_date, doc_lines)

    @api.model
    def document_check_budget(self, doc_date, doc_lines, amount_field=False,
                              internal_charge=False):
        res = {'budget_ok': True,
               'budget_status': {},
               'message': False}
        fiscal_id, budget_levels = self.get_fiscal_and_budget_level(doc_date)
        # Internal Charge, no budget check
        if internal_charge:
            fiscal = self.env['account.fiscalyear'].browse(fiscal_id)
            if fiscal.control_ext_charge_only:
                self = self.with_context(force_no_budget_check=True)
        # Validate Budget Level
        if not self._validate_budget_levels(budget_levels):
            return {'budget_ok': False,
                    'budget_status': {},
                    'message': 'Budget level(s) is not set!'}
        # Check for all budget types (unit base, project base, etc...)
        for budget_type in dict(self.BUDGET_LEVEL_TYPE).keys():
            budget_level = budget_levels[budget_type]
            # For document line within this fiscal_id only
            doc_lines = filter(lambda x:
                               not x.get('fiscalyear_id', False) or
                               x['fiscalyear_id'] == fiscal_id, doc_lines)
            if not doc_lines:
                continue
            vals = list(set([x[budget_level] for x in doc_lines]))
            res_ids = list(filter(lambda a: a is not False, vals))
            for res_id in res_ids:
                filtered_lines = filter(lambda a: a[budget_level] == res_id,
                                        doc_lines)
                amount = 0.0
                if amount_field:
                    amount = sum(map(lambda l:
                                     l[amount_field], filtered_lines))
                    amount = self._calc_amount_company_currency(amount)
                res = self.check_budget(fiscal_id,
                                        budget_type,  # eg, project_base
                                        budget_level,  # eg, project_id
                                        res_id,
                                        amount)
                if not res['budget_ok']:
                    return res
        return res

    @api.model
    def simple_check_budget(self, doc_date, budget_type,
                            amount, res_id,
                            internal_charge=False
                            ):
        """ This method is used to check budget of one type and one res_id
            :param date: doc_date, document date or date to check budget
            :param budget_type: 1 of the 5 budget types
            :param amount: Check amount, to just check status, use False
            :param res_id: resource's id, differ for each type of budget
            :return: dict of result
        """
        res = {'budget_ok': True,
               'budget_status': {},
               'message': False,
               'force_no_budget_check': False}
        fiscal_id, budget_levels = self.get_fiscal_and_budget_level(doc_date)
        # Internal Charge, no budget check
        if isinstance(internal_charge, basestring):
            # Because java may pass as string
            internal_charge = \
                internal_charge.lower() == "true" and True or False
        if internal_charge:
            fiscal = self.env['account.fiscalyear'].browse(fiscal_id)
            if fiscal.control_ext_charge_only:
                self = self.with_context(force_no_budget_check=True)
        # Validate Budget Level
        if not self._validate_budget_levels(budget_levels):
            return {'budget_ok': False,
                    'budget_status': {},
                    'message': 'Budget level(s) is not set!',
                    'force_no_budget_check': False,
                    }
        # Check for single budget type
        budget_level = budget_levels[budget_type]
        amount = self._calc_amount_company_currency(amount)
        res = self.check_budget(fiscal_id,
                                budget_type,  # eg, project_base
                                budget_level,  # eg, project_id
                                res_id,
                                amount
                                # ext_field=ext_field,
                                # ext_res_id=ext_res_id
                                )
        return res

    @api.model
    def _validate_budget_levels(self, budget_levels):
        """ Simply validate that all budget level are setup properly """
        if False in budget_levels.values():
            return False
        for budget_type in dict(self.BUDGET_LEVEL_TYPE).keys():
            if budget_type not in budget_levels:
                return False
        return True

    # @api.model
    # def _prepare_sel_budget_fields(self, budget_type, budget_level):
    #     """ For level fund, will be 2 fields comination to check budget """
    #     sel_fields = [budget_level]
    #     if budget_level == 'fund_id':
    #         budget_type_dict = {
    #             'unit_base': 'section_id',
    #             'project_base': 'project_id',
    #             'personnel': 'personnel_costcenter_id',
    #             'invest_asset': 'investment_asset_id',
    #             'invest_construction': 'invest_construction_phase_id'}
    #         sel_fields.append(budget_type_dict[budget_type])
    #     return sel_fields

    @api.model
    def _calc_amount_company_currency(self, amount):
        currency_id = self._context.get('currency_id', False)
        if currency_id and amount is not False:
            currency = self.env['res.currency'].browse(currency_id)
            company_currency = self.env.user.company_id.currency_id
            if company_currency != currency:
                amount = currency.compute(amount, company_currency)
        return amount

    @api.multi
    def _get_past_consumed_domain(self):
        self.ensure_one()
        dom = super(AccountBudget, self)._get_past_consumed_domain()
        # Level of Budget Control Sheet
        budget_type_dict = {
            'unit_base': 'section_id',
            'project_base': 'program_id',
            'personnel': False,
            'invest_asset': 'org_id',
            'invest_construction': 'org_id'}
        dimension = budget_type_dict.get(self.chart_view, False)
        dom += [('chart_view', '=', self.chart_view)]
        if dimension:
            dom.append((dimension, '=', self[dimension].id))
        return dom

    @api.multi
    def _compute_commitment_summary_line_ids(self):
        """ Overwrite """
        CHART_VIEWS = {'unit_base': 'section_id',
                       'project_base': 'program_id',
                       'personnel': False,
                       'invest_asset': 'org_id',
                       'invest_construction': 'org_id'}
        Commitment = self.env['budget.commitment.summary']
        for budget in self:
            if not budget.chart_view:
                continue
            field = CHART_VIEWS[budget.chart_view]
            domain = [('fiscalyear_id', '=', budget.fiscalyear_id.id),
                      ('all_commit', '!=', 0.0),
                      ('chart_view', '=', budget.chart_view)]
            if field:
                domain.append((field, '=', budget[field].id))
            budget.commitment_summary_expense_line_ids = \
                Commitment.search(domain + [('budget_method', '=', 'expense')])
            budget.commitment_summary_revenue_line_ids = \
                Commitment.search(domain + [('budget_method', '=', 'revenue')])


class AccountBudgetLine(models.Model):
    _inherit = 'account.budget.line'

    budget_release = fields.Selection(
        selection_add=[('auto_rolling', 'Auto Release as Rolling')],
    )

    @api.multi
    def _get_past_actual_amount(self):
        """ For auto rolling, only invest asset is allowed """
        """ Will avaliable only if line unique with chart_view """
        budget_type_dict = {
            # 'unit_base': False,
            # 'project_base': False,
            # 'personnel': False,
            # 'invest_construction': False,
            'invest_asset': 'invest_asset_id',
        }
        self.ensure_one()
        if self.chart_view not in budget_type_dict.keys():
            raise ValidationError(
                _('This budget (%s) can not use release by rolling') %
                (self.chart_view, ))
        dimension = budget_type_dict[self.chart_view]
        dom = [('budget_method', '=', 'expense'),
               ('chart_view', '=', self.chart_view),
               ('fiscalyear_id', '=', self.fiscalyear_id.id),
               (dimension, '=', self[dimension].id),
               ]
        sql = """
            select coalesce(sum(amount_actual), 0.0) amount_actual
            from budget_consume_report where %s
        """ % self.env['account.budget']._domain_to_where_str(dom)
        self._cr.execute(sql)
        amount = self._cr.fetchone()[0]
        return amount

    @api.multi
    def _get_future_plan_amount(self):
        self.ensure_one()
        Period = self.env['account.period']
        period_num = 0
        this_period_date_start = Period.find().date_start
        if self.fiscalyear_id.date_start > this_period_date_start:
            period_num = 0
        elif self.fiscalyear_id.date_stop < this_period_date_start:
            period_num = 12
        else:
            period_num = Period.get_num_period_by_period()
        future_plan = 0.0
        for line in self:
            for i in range(period_num + 1, 13):
                future_plan += line['m%s' % (i,)]
        return future_plan

    @api.multi
    def auto_release_budget(self):
        super(AccountBudgetLine, self).auto_release_budget()
        for line in self:
            budget_release = line.budget_id.budget_level_id.budget_release
            if line.id and budget_release == 'auto_rolling':
                past_consumed = line._get_past_actual_amount()
                future_plan = line._get_future_plan_amount()
                rolling = past_consumed + future_plan
                self._cr.execute("""
                    update account_budget_line set released_amount = %s
                    where id = %s
                """, (rolling, line.id))
