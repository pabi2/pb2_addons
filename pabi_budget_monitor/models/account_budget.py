# -*- coding: utf-8 -*-
from openerp import models, api


class AccountBudget(models.Model):
    _inherit = 'account.budget'

    BUDGET_LEVEL = {
        'activity_group_id': 'Activity Group',
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
        'personnel_costcenter_id': 'Personnel Costcenter',
        # Investment
        # - Asset
        'invest_asset_categ_id': 'Invest. Asset Category',
        'invest_asset_id': 'Invest. Asset',
        # - Construction
        'invest_construct_id': 'Construction',
        'invest_construct_phase_id': 'Construction Phase',
    }

    BUDGET_LEVEL_MODEL = {
        'activity_group_id': 'account.activity.group',
        # 'activity_id': 'Activity'  # No Activity Level{
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
        'personnel_costcenter_id': 'res.personnel.costceter',
        # Investment
        # - Asset
        'invest_asset_categ_id': 'res.invest.asset.category',
        'invest_asset_id': 'res.invest.asset',
        # - Construction
        'invest_construction_id': 'res.invest.construction',
        'invest_construction_phase_id': 'res.invest.construction.phase',
    }

    BUDGET_LEVEL_TYPE = {
        'check_budget_project_create': 'Project Creation',
        'check_budget_project_base': 'Project Based',
        'check_budget_unit_base': 'Unit Based',
        'check_budget_personnel': 'Personnel',
        'check_budget_invest_asset': 'Investment Asset',
        'check_budget_invest_construction': 'Investment Construction',
    }

    @api.one
    def _validate_budget_level(self, budget_type='check_budget'):
        if self.chart_view == 'project_base':
            budget_type = 'check_budget_project_base'
        if self.chart_view == 'unit_base':
            budget_type = 'check_budget_unit_base'
        super(AccountBudget, self)._validate_budget_level(budget_type)

    # -- Budget Check --
    @api.model
    def _get_budget_monitor(self, fiscal, budget_type,
                            budget_level, resource, pu_id=False):
        """ Overwrite """
        if budget_type not in ['check_budget_unit_base',
                               'check_budget_project_base']:
            return super(AccountBudget, self)._get_budget_monitor(fiscal,
                                                                  budget_level,
                                                                  resource,
                                                                  pu_id)
        monitors = False
        if budget_level in ('activity_group_id', 'activity_id'):
            if budget_type == 'check_budget_unit_base':
                monitors = resource.monitor_unit_ids.\
                    filtered(lambda x: x.fiscalyear_id == fiscal).\
                    filtered(lambda x: x['costcenter_id'].id == pu_id)
            elif budget_type == 'check_budget_project_base':
                monitors = resource.monitor_ids.\
                    filtered(lambda x: x.fiscalyear_id == fiscal).\
                    filtered(lambda x: x['project_id'].id == pu_id)
        else:
            monitors = resource.monitor_ids.\
                filtered(lambda x: x.fiscalyear_id == fiscal)
        return monitors
