# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.addons.pabi_chartfield.models.chartfield import CHART_VIEW_LIST


class BudgetMonitorReportWizard(models.TransientModel):
    _name = 'budget.monitor.report.wizard'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscalyear',
        default=lambda self: self.env['account.fiscalyear'].find(),
    )
    # from_period_id = fields.Many2one(
    #     'account.period',
    #     string='Period',
    # )
    # to_period_id = fields.Many2one(
    #     'account.period',
    #     string='To Period',
    # )
    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        string='Budget View',
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
    )
    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
    )
    groupby_quarter = fields.Boolean(
        string='Quarter',
        default=False,
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
    section_program_id = fields.Many2one(
        'res.section.program',
        string='Section Program',
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
    # Personnel Costcenter
    personnel_costcenter_id = fields.Many2one(
        'res.personnel.costcenter',
        string='Personnel Costcenter',
    )
    # Investment Asset
    invest_asset_id = fields.Many2one(
        'res.invest.asset',
        string='Investment Asset',
    )
    groupby_invest_asset = fields.Boolean(
        string='Investment Asset',
        default=False,
    )
    # Investment Construction
    invest_construction_id = fields.Many2one(
        'res.invest.construction',
        string='Project C',
    )
    invest_construction_phase_id = fields.Many2one(
        'res.invest.construction.phase',
        string='Phase',
    )
    groupby_invest_construction = fields.Boolean(
        string='Project C',
        default=False,
    )
    line_filter = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    chartfield_ids = fields.Many2many(
        'chartfield.view',
        string='Budget',
        domain=[('model', '!=', 'res.personnel.costcenter')],
    )

    @api.onchange('line_filter')
    def _onchange_line_filter(self):
        self.chartfield_ids = []
        Chartfield = self.env['chartfield.view']
        dom = []
        if self.line_filter:
            codes = self.line_filter.split('\n')
            codes = [x.strip() for x in codes]
            codes = ','.join(codes)
            dom.append(('code', 'ilike', codes))
            self.chartfield_ids = Chartfield.search(dom, order='id')

    @api.model
    def _get_filter_header(self):
        domain = []
        if self.chart_view:
            domain.append(('chart_view', '=', self.chart_view))
        if self.budget_method:
            domain.append(('budget_method', '=', self.budget_method))
        if self.fiscalyear_id:
            domain.append(('fiscalyear_id', '=', self.fiscalyear_id.id))
        # if self.from_period_id:
        #     domain.append(('period_id.date_start', '>=',
        #                    self.from_period_id.date_start))
        # if self.to_period_id:
        #     domain.append(('period_id.date_stop', '<=',
        #                    self.to_period_id.date_stop))
        # Budgets
        chartfield = self.chartfield_ids
        if chartfield:
            section_ids = chartfield.filtered(lambda l: l.type == 'sc:').ids
            project_ids = chartfield.filtered(lambda l: l.type == 'pj:').ids
            invest_construction_phase_ids = \
                chartfield.filtered(lambda l: l.type == 'cp:').ids
            invest_asset_ids = \
                chartfield.filtered(lambda l: l.type == 'ia:').ids
            personnel_costcenter_ids = \
                chartfield.filtered(lambda l: l.type == 'pc:').ids
            # --
            null_value = [0, 0]
            section_ids.extend(null_value)
            project_ids.extend(null_value)
            invest_construction_phase_ids.extend(null_value)
            invest_asset_ids.extend(null_value)
            personnel_costcenter_ids.extend(null_value)
            self._cr.execute("""
                select id
                from budget_monitor_report
                where section_id + 1000000 in %s or project_id + 2000000 in %s
                    or invest_construction_phase_id + 3000000 in %s or
                    invest_asset_id + 4000000 in %s or
                    personnel_costcenter_id + 5000000 in %s
            """ % (str(tuple(section_ids)), str(tuple(project_ids)),
                   str(tuple(invest_construction_phase_ids)),
                   str(tuple(invest_asset_ids)),
                   str(tuple(personnel_costcenter_ids))))
            ids = map(lambda l: l[0], self._cr.fetchall())
            domain.append(('id', 'in', ids))
        return domain

    @api.model
    def _get_filter_by_chart_view(self):
        chart_view_dict = {
            'unit_base': ['org_id', 'sector_id', 'subsector_id',
                          'division_id', 'section_id', 'charge_type',
                          'section_program_id'],
            'project_base': ['functional_area_id', 'program_group_id',
                             'program_id', 'project_group_id', 'project_id',
                             'charge_type', 'org_id', 'sector_id',
                             'subsector_id', 'division_id', 'section_id'],
            'invest_asset': ['invest_asset_id', 'charge_type', 'org_id',
                             'sector_id', 'subsector_id', 'division_id',
                             'section_id'],
            'invest_construction': ['invest_construction_phase_id',
                                    'charge_type', 'org_id', 'sector_id',
                                    'subsector_id', 'division_id',
                                    'section_id'],
            'personnel': ['personnel_costcenter_id'],
        }
        domain = []
        if not self.chart_view:
            if self.charge_type:
                domain.append(('charge_type', '=', self.charge_type))
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
            if self.section_program_id:
                domain.append(('section_program_id', '=',
                               self.section_program_id.id))
            return domain
        todos = chart_view_dict[self.chart_view]
        for field in todos:
            if self[field] and field != 'charge_type':
                domain.append((field, '=', self[field].id))
            elif field == 'charge_type' and self.charge_type:
                domain.append((field, '=', self.charge_type))
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

    @api.model
    def _get_groupby_invest_asset(self):
        res = {}
        if self.chart_view != 'invest_asset':
            return res
        if self.groupby_org:
            res.update({'search_default_groupby_org': True})
        if self.groupby_invest_asset:
            res.update({'search_default_groupby_invest_asset': True})
        return res

    @api.model
    def _get_groupby_invest_construction(self):
        res = {}
        if self.chart_view != 'invest_construction':
            return res
        if self.groupby_org:
            res.update({'search_default_groupby_org': True})
        if self.groupby_invest_construction:
            res.update({'search_default_groupby_invest_construction': True})
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
        result['context'].update(self._get_groupby_invest_asset())
        result['context'].update(self._get_groupby_invest_construction())
        # Update report name
        report_name = _('Budget Monitor %s %s %s') % \
            (dict(CHART_VIEW_LIST).get(self.chart_view),
             self.fiscalyear_id.name,
             self.org_id.name)
        result.update({'display_name': report_name})
        result.update({'name': report_name})
        return result

        @api.onchange('chart_view')
        def _onchange_chart_view_filter(self):
            self.charge_type = False
            self.personnel_costcenter_id = False
            self.invest_asset_id = False
            self.org_id = False
            self.sector_id = False
            self.subsector_id = False
            self.division_id = False
            self.section_id = False
            self.functional_area_id = False
            self.program_group_id = False
            self.program_id = False
            self.project_group_id = False
            self.project_id = False
            self.invest_construction_phase_id = False
            self.groupby_org = False
            self.groupby_sector = False
            self.groupby_subsector = False
            self.groupby_division = False
            self.groupby_section = False
            self.groupby_functional_area = False
            self.groupby_program_group = False
            self.groupby_program = False
            self.groupby_project_group = False
            self.groupby_project = False
            self.groupby_invest_asset = False
            self.groupby_invest_construction = False
