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
    'invest_asset': ['org_id', 'division_id', 'section_id'],
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

    @api.onchange('report_type')
    def _onchange_report_type(self):
        self.charge_type = False
        self.org_id = False
        self.sector_id = False
        self.subsector_id = False
        self.division_id = False
        self.section_id = False
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
        self.sector_id = False
        self.subsector_id = False
        self.division_id = False
        self.section_id = False

    @api.onchange('sector_id')
    def _onchange_sector_id(self):
        self.org_id = False
        self.subsector_id = False
        self.division_id = False
        self.section_id = False

    @api.onchange('subsector_id')
    def _onchange_subsector_id(self):
        self.org_id = False
        self.sector_id = False
        self.division_id = False
        self.section_id = False

    @api.onchange('division_id')
    def _onchange_division_id(self):
        self.org_id = False
        self.sector_id = False
        self.subsector_id = False
        self.section_id = False

    @api.onchange('section_id')
    def _onchange_section_id(self):
        self.org_id = False
        self.sector_id = False
        self.subsector_id = False
        self.division_id = False

    @api.onchange('functional_area_id')
    def _onchange_functional_area_id(self):
        self.program_group_id = False
        self.program_id = False
        self.project_group_id = False
        self.project_id = False

    @api.onchange('program_group_id')
    def _onchange_program_group_id(self):
        self.functional_area_id = False
        self.program_id = False
        self.project_group_id = False
        self.project_id = False

    @api.onchange('program_id')
    def _onchange_program_id(self):
        self.functional_area_id = False
        self.program_group_id = False
        self.project_group_id = False
        self.project_id = False

    @api.onchange('project_group_id')
    def _onchange_project_group_id(self):
        self.functional_area_id = False
        self.program_group_id = False
        self.program_id = False
        self.project_id = False

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.functional_area_id = False
        self.program_group_id = False
        self.program_id = False
        self.project_group_id = False
