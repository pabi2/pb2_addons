# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.addons.pabi_chartfield.models.chartfield import CHART_VIEW_LIST


class BudgetMonitorReportWizard(models.TransientModel):
    _name = 'budget.monitor.report.wizard'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )
    from_period_id = fields.Many2one(
        'account.period',
        string='Period',
    )
    to_period_id = fields.Many2one(
        'account.period',
        string='To Period',
    )
    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        string='Budget View',
    )
    # Unit Base
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    sector_id = fields.Many2one(
        'res.sector',
        string='Sector',
    )
    subsector_id = fields.Many2one(
        'res.subsector',
        string='Subsector',
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    groupby_org = fields.Boolean(
        string='Org',
        default=False,
    )
    groupby_sector = fields.Boolean(
        string='Sector',
        default=False,
    )
    groupby_subsector = fields.Boolean(
        string='Subsector',
        default=False,
    )
    groupby_division = fields.Boolean(
        string='Division',
        default=False,
    )
    groupby_section = fields.Boolean(
        string='Section',
        default=False,
    )
    # Project Base
    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Functional Area',
    )
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group',
    )
    program_id = fields.Many2one(
        'res.program',
        string='Program',
    )
    project_group_id = fields.Many2one(
        'res.project.group',
        string='Project Group',
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
    )
    groupby_functional_area = fields.Boolean(
        string='Functional Area',
        default=False,
    )
    groupby_program_group = fields.Boolean(
        string='Program Group',
        default=False,
    )
    groupby_program = fields.Boolean(
        string='Program',
        default=False,
    )
    groupby_project_group = fields.Boolean(
        string='Project Group',
        default=False,
    )
    groupby_project = fields.Boolean(
        string='Project',
        default=False,
    )

    @api.model
    def _get_filter_header(self):
        domain = []
        if self.chart_view:
            domain.append(('chart_view', '=', self.chart_view))
        if self.fiscalyear_id:
            domain.append(('fiscalyear_id', '=', self.fiscalyear_id.id))
        if self.from_period_id:
            domain.append(('from_period_id', '=', self.from_period_id.id))
        if self.to_period_id:
            domain.append(('to_period_id', '=', self.to_period_id.id))
        return domain

    @api.model
    def _get_filter_unit_base(self):
        domain = []
        if self.org_id:
            domain.append(('org_id', '=', self.org_id.id))
        if self.sector_id:
            domain.append(('sector_id', '=', self.sector_id.id))
        if self.subsector_id:
            domain.append(('subsector_id', '=', self.subsector_id.id))
        if self.division_id:
            domain.append(('division_id', '=', self.division_id.id))
        if self.section_id:
            domain.append(('section_id', '=', self.section_id.id))
        return domain

    @api.model
    def _get_filter_project_base(self):
        domain = []
        if self.functional_area_id:
            domain.append(('functional_area_id', '=',
                           self.functional_area_id.id))
        if self.program_group_id:
            domain.append(('program_group_id', '=', self.program_group_id.id))
        if self.program_id:
            domain.append(('program_id', '=', self.program_id.id))
        if self.project_group_id:
            domain.append(('project_group_id', '=', self.project_group_id.id))
        if self.project_id:
            domain.append(('project_id', '=', self.project_id.id))
        return domain

    @api.model
    def _get_filter_by_chart_view(self):
        chart_view_dict = {
            'unit_base': ['org_id', 'sector_id', 'subsector_id',
                          'division_id', 'section_id'],
            'project_base': ['functional_area_id', 'program_group_id',
                             'program_id', 'project_group_id', 'project_id'],
            'invest_asset': [],
            'invest_construction': [],
            'personnel': [],
        }
        domain = []
        if not self.chart_view:
            return domain
        todos = chart_view_dict[self.chart_view]
        for field in todos:
            if self[field]:
                domain.append((field, '=', self[field].id))
        return domain

    @api.model
    def _get_groupby_unit_base(self):
        res = {}
        if self.chart_view != 'unit_base':
            return res
        if self.groupby_org:
            res.update({'search_default_groupby_org': True})
        if self.groupby_sector:
            res.update({'search_default_groupby_sector': True})
        if self.groupby_subsector:
            res.update({'search_default_groupby_subsector': True})
        if self.groupby_division:
            res.update({'search_default_groupby_division': True})
        if self.groupby_section:
            res.update({'search_default_groupby_section': True})
        return res

    @api.model
    def _get_groupby_project_base(self):
        res = {}
        if self.chart_view != 'project_base':
            return res
        if self.groupby_functional_area:
            res.update({'search_default_groupby_functional_area': True})
        if self.groupby_program_group:
            res.update({'search_default_groupby_program_group': True})
        if self.groupby_program:
            res.update({'search_default_groupby_program': True})
        if self.groupby_project_group:
            res.update({'search_default_groupby_project_group': True})
        if self.groupby_project:
            res.update({'search_default_groupby_project': True})
        return res

    @api.multi
    def open_report(self):
        self.ensure_one()
        action = self.env.ref('account_budget_activity.'
                              'action_budget_monitor_report')
        result = action.read()[0]
        # Get filter
        domain = []
        domain += self._get_filter_header()
        domain += self._get_filter_by_chart_view()
        # domain += self._get_filter_unit_base()
        # domain += self._get_filter_project_base()
        result.update({'domain': domain})
        # Group by
        result['context'] = {}
        result['context'].update(self._get_groupby_unit_base())
        result['context'].update(self._get_groupby_project_base())
        # Update report name
        report_name = _('Budget Monitor %s %s %s') % \
            (dict(CHART_VIEW_LIST).get(self.chart_view),
             self.fiscalyear_id.name,
             self.org_id.name)
        result.update({'display_name': report_name})
        result.update({'name': report_name})
        return result
