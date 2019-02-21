# -*- coding: utf-8 -*-
from openerp import api, fields
from openerp.addons.pabi_chartfield.models.chartfield import ChartField

REPORT_TYPES = [('all', 'All'),
                ('overall', 'Overall'),
                ('unit_base', 'Section'),
                ('project_base', 'Project'),
                ('invest_asset', 'Asset'),
                ('invest_construction', 'Construction'),
                ('personnel', 'Personnel')]

REPORT_GROUPBY = {
    'all': [],
    'unit_base': ['section_id', 'activity_group_id',
                  'charge_type', 'activity_id'],
    'project_base': ['project_id', 'activity_group_id',
                     'charge_type', 'activity_id'],
    'invest_asset': ['org_id', 'invest_asset_id'],
    'invest_construction': ['org_id', 'invest_construction_id',
                            'invest_construction_phase_id'],
    'personnel': ['org_id', 'personnel_costcenter_id',
                  'activity_group_id', 'activity_id']
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
        selection=lambda self: self._get_report_type(),
        string='Report Type',
        required=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,  # Overwrite as requried field.
    )
    # ------------ SEARCH ------------
    # For All
    chartfield_id = fields.Many2one(
        'chartfield.view',
        string='Budget',
    )
    chartfield_ids = fields.Many2many(
        'chartfield.view',
        string='Budgets',
        domain=[('model', '!=', 'res.personnel.costcenter')],
    )
    section_program_id = fields.Many2one(
        'res.section.program',
        string='Section Program',
    )
    # For: Overall
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
    personnel_costcenter_id = fields.Many2one(
        'res.personnel.costcenter'
    )
    # Group By
    group_by_chartfield_id = fields.Boolean(
        string='Group By - Budget',
        default=False,
    )
    group_by_section_id = fields.Boolean(
        string='Group By - Section',
        default=False,
    )
    group_by_project_id = fields.Boolean(
        string='Group By - Project',
        default=False,
    )
    group_by_personnel_costcenter_id = fields.Boolean(
        string='Group By - Personnel Budget',
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
    group_by_invest_construction_id = fields.Boolean(
        string='Group By - Project C',
        default=False,
    )
    group_by_invest_construction_phase_id = fields.Boolean(
        string='Group By - Project Phase',
        default=False,
    )
    # group_by_personnel_budget_id = fields.Boolean(
    #     string='Group By - Personnel Budget',
    #     default=False,
    # )
    # For my budget report
    section_ids = fields.Many2many(
        'res.section',
        string='Section',
        domain=lambda self: self._get_domain_section(),
    )
    project_ids = fields.Many2many(
        'res.project',
        string='Project',
        domain=lambda self: self._get_domain_project(),
    )
    action_type = fields.Selection(
        [('budget_overview_report', 'Budget Overview Report'),
         ('my_budget_report', 'My Budget Report')],
        string='Action Type',
    )

    @api.model
    def _get_report_type(self):
        report_types = REPORT_TYPES
        if self._context.get('action_type', False) == 'my_budget_report':
            report_types = [('unit_base', 'Section'),
                            ('project_base', 'Project')]
        return report_types

    @api.model
    def _get_domain_section(self):
        section_ids = []
        Section = self.env['res.section']
        # Group
        module = 'pabi_budget_drilldown_report'
        see_own_section = '%s.%s' % (module, 'group_unit_base_see_own_section')
        see_own_division = \
            '%s.%s' % (module, 'group_unit_base_see_own_division')
        see_own_subsector = \
            '%s.%s' % (module, 'group_unit_base_see_own_subsector')
        see_own_sector = '%s.%s' % (module, 'group_unit_base_see_own_sector')
        see_own_org = '%s.%s' % (module, 'group_unit_base_see_own_org')
        see_all_org = '%s.%s' % (module, 'group_unit_base_see_all_org')
        # Domain
        user = self.env.user
        if user.has_group(see_own_section):
            section_ids.extend([user.employee_id.section_id.id])
        if user.has_group(see_own_division):
            division_id = user.employee_id.section_id.division_id.id
            if self._name == 'budget.drilldown.report.wizard':
                section = Section.search([('division_id', '=', division_id),'|',('active','=',True),('active','=',False)])
            else:
                section = Section.search([('division_id', '=', division_id)])
            section_ids.extend(section.ids)
        if user.has_group(see_own_subsector):
            subsector_id = user.employee_id.section_id.subsector_id.id
            if self._name == 'budget.drilldown.report.wizard':
                section = Section.search([('subsector_id', '=', subsector_id),'|',('active','=',True),('active','=',False)])
            else:
                section = Section.search([('subsector_id', '=', subsector_id)])
            section_ids.extend(section.ids)
        if user.has_group(see_own_sector):
            sector_id = user.employee_id.section_id.sector_id.id
            if self._name == 'budget.drilldown.report.wizard':
                section = Section.search([('sector_id', '=', sector_id),'|',('active','=',True),('active','=',False)])
            else:
                section = Section.search([('sector_id', '=', sector_id)])
            section_ids.extend(section.ids)
        if user.has_group(see_own_org):
            org_id = user.employee_id.section_id.org_id.id
            if self._name == 'budget.drilldown.report.wizard':
                section = Section.search([('org_id', '=', org_id),'|',('active','=',True),('active','=',False)])
            else:
                section = Section.search([('org_id', '=', org_id)])
            section_ids.extend(section.ids)
        if user.has_group(see_all_org):
            if self._name == 'budget.drilldown.report.wizard':
                section = Section.search(['|',('active','=',True),('active','=',False)])
            else:
                section = Section.search([])
            section_ids.extend(section.ids)
        if self._name == 'budget.drilldown.report.wizard':
                section_ids = list(set(filter(lambda l: l, section_ids)))
        else:
            section_ids = list(set(filter(lambda l: l is not False, section_ids)))
        return [('id', 'in', section_ids)]

    @api.model
    def _get_domain_project(self):
        Member = self.env['res.project.member']
        Project = self.env['res.project']
        # Group
        module = 'pabi_budget_drilldown_report'
        see_own_project_division = \
            '%s.%s' % (module, 'group_project_base_see_own_project_division')
        # Domain
        user = self.env.user
        employee_id = user.employee_id.id

        # --
        member = Member.search([('employee_id', '=', employee_id)])
        self._cr.execute("""
            select project_id from project_hr_employee_rel where employee_id =
            %s""" % (employee_id or 0, ))
        project_ids = \
            Project.browse(map(lambda l: l[0], self._cr.fetchall())).ids + \
            Project.search([('analyst_employee_id', '=', employee_id)]).ids + \
            Project.search([('pm_employee_id', '=', employee_id)]).ids + \
            [x.project_id.id for x in member]

        # --
        if user.has_group(see_own_project_division):
            division_id = user.employee_id.section_id.division_id.id
            project = Project.search([('owner_division_id', '=', division_id)])
            project_ids.extend(project.ids)
        project_ids = list(set(filter(lambda l: l is not False, project_ids)))
        return [('id', 'in', project_ids)]

    @api.onchange('report_type')
    def _onchange_report_type(self):
        # For budget overview report
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
        self.chartfield_id = False
        self.chartfield_ids = False
        self.section_program_id = False
        # For my budget report
        self.section_ids = False
        self.project_ids = False

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
