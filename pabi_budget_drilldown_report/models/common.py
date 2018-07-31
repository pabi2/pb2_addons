# -*- coding: utf-8 -*-
from openerp import api, fields
from openerp.addons.pabi_chartfield.models.chartfield import ChartField

REPORT_TYPES = [('overall', 'Overall'),
                ('unit_base', 'Section'),
                ('project_base', 'Project'),
                ('invest_asset', 'Asset'),
                ('invest_construction', 'Construction')]

REPORT_GROUPBY = {
    'unit_base': ['section_id', 'activity_group_id',
                  'charge_type', 'activity_id'],
    'project_base': ['project_id', 'activity_group_id',
                     'charge_type', 'activity_id'],
    'invest_asset': ['org_id', 'division_id', 'section_id', 'invest_asset_id'],
    'invest_construction': ['org_id', 'division_id',
                            'section_id', 'invest_construction_id'],
}


class SearchCommon(ChartField, object):
    """ This class add some common search options """

    budget_commit_type = fields.Selection(
        [('so_commit', 'SO Commitment'),
         ('pr_commit', 'PR Commitment'),
         ('po_commit', 'PO Commitment'),
         ('exp_commit', 'Expense Commitment'),
         ('actual', 'Actual'),
         ],
        string='Budget Commit Type',
    )
    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
    )
    report_type = fields.Selection(
        REPORT_TYPES,
        string='Report Type',
        required=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,  # Overwrite as requried field.
    )
    # ------------ SEARCH ------------
    # For: All report types
    org_id = fields.Many2one(
        'res.org',
        string='Orgs',
    )
    # For unit_base
    sector_id = fields.Many2one(
        'res.sector',
        string='Sector',
    )
    subsector_id = fields.Many2one(
        'res.subsector',
        string='Subsector',
    )
    # For project_base and invest_construction
    division_id = fields.Many2one(
        'res.division',
        string='Division',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    invest_construction_id = fields.Many2one(
        'res.invest.construction',
        string='Project (C)',
    )
    # For unit_base and invest_asset
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )
    invest_asset_id = fields.Many2one(
        'res.invest.asset',
        string='Investment Asset',
    )
    # For project_base
    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Functional Area'
    )
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group'
    )
    program_id = fields.Many2one(
        'res.program',
        string='Program'
    )
    project_group_id = fields.Many2one(
        'res.project.group',
        string='Project Group'
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project'
    )
    # Group By
    group_by_section_id = fields.Boolean(
        string='Group By - Section',
        default=False,
    )
    group_by_project_id = fields.Boolean(
        string='Group By - Project',
        default=False,
    )
    group_by_activity_group_id = fields.Boolean(
        string='Group By - Activity Group',
        default=False,
    )
    group_by_charge_type = fields.Boolean(
        string='Group By - Charge Type',
        default=False,
    )
    group_by_activity_id = fields.Boolean(
        string='Group By - Activity',
        default=False,
    )
    group_by_invest_asset_id = fields.Boolean(
        string='Group By - Asset',
        default=False,
    )
    group_by_org_id = fields.Boolean(
        string='Group By - Org',
        default=False,
    )
    group_by_division_id = fields.Boolean(
        string='Group By - Division',
        default=False,
    )
    group_by_invest_construction_id = fields.Boolean(
        string='Group By - Project C',
        default=False,
    )
    x = "org_id"

    @api.onchange('report_type')
    def _onchange_report_type(self):
        self.charge_type = False
        self.org_id = False
        self.sector_id = False
        self.subsector_id = False
        self.division_id = False
        self.section_id = False
        self.invest_asset_id = False
        self.activity_group_id = False
        self.activity_id = False
        self.functional_area_id = False
        self.program_group_id = False
        self.program_id = False
        self.project_group_id = False
        self.project_id = False
        self.invest_construction_id = False

    @api.onchange('org_id')
    def _onchange_org_id(self):
        if self.org_id:
            self.sector_id = False
            self.subsector_id = False
            self.division_id = False
            self.section_id = False

    @api.onchange('sector_id')
    def _onchange_sector_id(self):
        if self.sector_id:
            self.org_id = False
            self.subsector_id = False
            self.division_id = False
            self.section_id = False

    @api.onchange('subsector_id')
    def _onchange_subsector_id(self):
        if self.subsector_id:
            self.org_id = False
            self.sector_id = False
            self.division_id = False
            self.section_id = False

    @api.onchange('division_id')
    def _onchange_division_id(self):
        if self.division_id:
            self.org_id = False
            self.sector_id = False
            self.subsector_id = False
            self.section_id = False

    @api.onchange('section_id')
    def _onchange_section_id(self):
        if self.section_id:
            self.org_id = False
            self.sector_id = False
            self.subsector_id = False
            self.division_id = False

    @api.onchange('functional_area_id')
    def _onchange_functional_area_id(self):
        if self.functional_area_id:
            self.program_group_id = False
            self.program_id = False
            self.project_group_id = False
            self.project_id = False

    @api.onchange('program_group_id')
    def _onchange_program_group_id(self):
        if self.program_group_id:
            self.functional_area_id = False
            self.program_id = False
            self.project_group_id = False
            self.project_id = False

    @api.onchange('program_id')
    def _onchange_program_id(self):
        if self.program_id:
            self.functional_area_id = False
            self.program_group_id = False
            self.project_group_id = False
            self.project_id = False

    @api.onchange('project_group_id')
    def _onchange_project_group_id(self):
        if self.project_group_id:
            self.functional_area_id = False
            self.program_group_id = False
            self.program_id = False
            self.project_id = False

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            self.functional_area_id = False
            self.program_group_id = False
            self.program_id = False
            self.project_group_id = False

    @api.onchange('activity_id')
    def _onchange_activity_id(self):
        if self.activity_id:
            self.activity_group_id = False

    @api.onchange('activity_group_id')
    def _onchange_activity_group_id(self):
        if self.activity_group_id:
            self.activity_id = False
