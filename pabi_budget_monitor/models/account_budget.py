# -*- coding: utf-8 -*-
from openerp import models, api, _


class AccountBudget(models.Model):
    _inherit = 'account.budget'

    BUDGET_LEVEL = {
        # Code not cover Activity level yet
        # 'activity_group_id': 'Activity Group',
        # 'activity_id': 'Activity',
        # Fund
        # 'fund_id': 'Fund (for all)',
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
    def document_check_budget(self, doc_date, doc_lines, amount_field=False):
        res = {'budget_ok': True,
               'budget_status': {},
               'message': False}
        fiscal_id, budget_levels = self.get_fiscal_and_budget_level(doc_date)
        # Validate Budget Level
        if not self._validate_budget_levels(budget_levels):
            return {'budget_ok': False,
                    'budget_status': {},
                    'message': 'Budget level(s) is not set!'}
        # Check for all budget types (unit base, project base, etc...)
        for budget_type in dict(self.BUDGET_LEVEL_TYPE).keys():
            budget_level = budget_levels[budget_type]
            # For document only
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
                            amount, res_id):
        """ This method is used to check budget of one type and one res_id
            :param date: doc_date, document date or date to check budget
            :param budget_type: 1 of the 5 budget types
            :param amount: Check amount, to just check status, use False
            :param res_id: resource's id, differ for each type of budget
            :return: dict of result
        """
        res = {'budget_ok': True,
               'budget_status': {},
               'message': False}
        fiscal_id, budget_levels = self.get_fiscal_and_budget_level(doc_date)
        # Validate Budget Level
        if not self._validate_budget_levels(budget_levels):
            return {'budget_ok': False,
                    'budget_status': {},
                    'message': 'Budget level(s) is not set!'}
        # Check for single budget type
        budget_level = budget_levels[budget_type]
        # sel_fields = self._prepare_sel_budget_fields(budget_type,
        #                                              budget_level)
        # ext_res_id = False
        # ext_field = False
        # if len(sel_fields) > 1 and 'fund_id' in sel_fields:
        #     if not fund_id:
        #         return {'budget_ok': False,
        #                 'budget_status': {},
        #                 'message': 'Fund is not selected!'}
        #     else:
        #         ext_field = len(sel_fields) == 2 and sel_fields[1] or False
        #         # Reassign
        #         ext_res_id = res_id
        #         res_id = fund_id

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
            'personnel': 'personnel_costcenter_id',  # TODO: ???
            'invest_asset': 'org_id',
            'invest_construction': 'org_id'}
        dimension = budget_type_dict[self.chart_view]
        dom += [('chart_view', '=', self.chart_view),
                (dimension, '=', self[dimension].id)]
        return dom

    @api.multi
    def _compute_commitment_summary_line_ids(self):
        """ Overwrite """
        Commitment = self.env['budget.commitment.summary']
        for budget in self:
            if not budget.section_id:  # Extra
                continue
            domain = [('fiscalyear_id', '=', budget.fiscalyear_id.id),
                      ('all_commit', '!=', 0.0),
                      ('section_id', '=', budget.section_id.id)]  # Extra
            budget.commitment_summary_expense_line_ids = \
                Commitment.search(domain + [('budget_method', '=', 'expense')])
            budget.commitment_summary_revenue_line_ids = \
                Commitment.search(domain + [('budget_method', '=', 'revenue')])
