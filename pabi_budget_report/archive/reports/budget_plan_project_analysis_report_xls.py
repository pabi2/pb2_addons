# -*- coding: utf-8 -*
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell
from openerp.report import report_sxw
from openerp.tools.translate import _
import xlwt
import datetime

C_OR_N = {
    'continue': 'Continue',
    'new': 'New',
}

PROJECT_KIND = {
    'research': 'Research',
    'non_research': 'Non-Research',
    'management': 'Management',
    'construction': 'Construction',
}

EXTERNAL_FUND_TYPE = {
    'government': 'Government',
    'private': 'Private Organization',
    'oversea': 'Oversea',
}

BUDGET_METHOD = {
    'revenue': 'Revenue',
    'expense': 'Expense',
}

COLUMN_SIZES = [
    ('project', 25),
    ('name', 25),
    ('c_or_n', 25),
    ('functional_area', 25),
    ('program', 25),
    ('project_group', 25),
    ('nstda_strategy', 25),
    ('project_objective', 25),
    ('section_program', 25),
    ('mission', 25),
    ('project_kind', 25),
    ('project_type', 25),
    ('org', 25),
    ('costcenter', 25),
    ('owner_division', 25),
    ('pm_employee', 25),
    ('budget_method', 25),
    ('date_start', 25),
    ('date_end', 25),
    ('project_duration', 25),
    ('project_status', 25),
    ('analyst_employee', 25),
    ('ref_program', 25),
    ('external_fund_type', 25),
    ('external_fund_name', 25),
    ('priority', 25),
    ('fy1', 25),
    ('fy2', 25),
    ('fy3', 25),
    ('fy4', 25),
    ('fy5', 25),
    ('revenue_budget', 25),
    ('overall_revenue_plan', 25),
    ('pfm_publications', 25),
    ('pfm_patents', 25),
    ('pfm_petty_patents', 25),
    ('pfm_copyrights', 25),
    ('pfm_trademarks', 25),
    ('pfm_plant_varieties', 25),
    ('pfm_laboratory_prototypes', 25),
    ('pfm_field_prototypes', 25),
    ('pfm_commercial_prototypes', 25),
    ('overall_revenue', 25),
    ('current_revenue', 25),
    ('overall_expense_budget', 25),
    ('overall_actual', 25),
    ('overall_commit', 25),
    ('overall_expense_balance', 25),
    ('planned', 25),
    ('released', 25),
    ('all_commit', 25),
    ('actual', 25),
    ('balance', 25),
    ('est_commit', 25),
    ('m1', 25),
    ('m2', 25),
    ('m3', 25),
    ('m4', 25),
    ('m5', 25),
    ('m6', 25),
    ('m7', 25),
    ('m8', 25),
    ('m9', 25),
    ('m10', 25),
    ('m11', 25),
    ('m12', 25),
    ('planned_amount', 25),
]


class BudgetPlanProjectAnalysisReportXLSParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(BudgetPlanProjectAnalysisReportXLSParser, self).__init__(
            cr, uid, name, context=context)

        self.localcontext.update({
            'report_name': _('Budget Plan Analysis'),
        })

    def set_context(self, objects, data, ids, report_type=None):
        # Declare Valiable
        cr, uid = self.cr, self.uid

        # Get Data
        form = data.get('form', {})
        fiscalyear_id = form.get('fiscalyear_id', False)
        functional_area_id = form.get('functional_area_id', False)
        program_group_id = form.get('program_group_id', False)
        program_id = form.get('program_id', False)
        project_group_id = form.get('project_group_id', False)
        project_id = form.get('project_id', False)
        budget_method = form.get('budget_method', False)

        # Browse Fiscalyear
        Fiscalyear = self.pool.get('account.fiscalyear')
        fiscalyear = Fiscalyear.browse(cr, uid, fiscalyear_id)

        # Browse Structure
        FunctionalArea = self.pool.get('res.functional.area')
        ProgramGroup = self.pool.get('res.program.group')
        Program = self.pool.get('res.program')
        ProjectGroup = self.pool.get('res.project.group')
        Project = self.pool.get('res.project')
        functional_area = FunctionalArea.browse(cr, uid, functional_area_id)
        program_group = ProgramGroup.browse(cr, uid, program_group_id)
        program = Program.browse(cr, uid, program_id)
        project_group = ProjectGroup.browse(cr, uid, project_group_id)
        project = Project.browse(cr, uid, project_id)

        # Browse Report
        Report = self.pool.get('budget.plan.project.line')
        domain = [('fiscalyear_id', '=', fiscalyear_id)]
        if functional_area:
            domain += [('functional_area_id', '=', functional_area_id)]
        if program_group:
            domain += [('program_group_id', '=', program_group_id)]
        if program:
            domain += [('program_id', '=', program_id)]
        if project_group:
            domain += [('project_group_id', '=', project_group_id)]
        if project:
            domain += [('project_id', '=', project_id)]
        if budget_method:
            domain += [('budget_method', '=', budget_method)]
        report_ids = Report.search(cr, uid, domain)
        report = Report.browse(cr, uid, report_ids)

        # Update Context
        self.localcontext.update({
            'fiscalyear': fiscalyear,
            'functional_area': functional_area,
            'program_group': program_group,
            'program': program,
            'project_group': project_group,
            'project': project,
            'budget_method': budget_method,
            'report': report,
        })

        return \
            super(BudgetPlanProjectAnalysisReportXLSParser, self).set_context(
                objects, data, report_ids, report_type=report_type)


class BudgetPlanProjectAnalysisReportXLS(report_xls):
    column_sizes = [x[1] for x in COLUMN_SIZES]

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        ws = wb.add_sheet(_p.report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # Header
        cell_format = _xs['bold'] + _xs['borders_all']
        cell_style_title = xlwt.easyxf(
            cell_format + "pattern: pattern solid, fore_color ice_blue;")
        cell_style_value = xlwt.easyxf(
            cell_format + _xs['center'] + _xs['fill_blue'])
        c_specs = [
            ('financial_year_title', 1, 0, 'text', _('Financial Year'), None,
                cell_style_title),
            ('financial_year_value', 1, 0, 'text', _p.fiscalyear.name, None,
                cell_style_value),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        c_specs = [
            ('functional_area_title', 1, 0, 'text', _('Functional Area'),
                None, cell_style_title),
            ('functional_area_value', 1, 0, 'text',
                '%s%s' %
                (_p.functional_area.code and
                 '[' + _p.functional_area.code + '] ' or '',
                 _p.functional_area.name_short and
                 _p.functional_area.name_short or _p.functional_area.name
                 or ''),
             None, cell_style_value)
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        c_specs = [
            ('program_group_title', 1, 0, 'text', _('Program Group'), None,
                cell_style_title),
            ('program_group_value', 1, 0, 'text',
                '%s%s' %
                (_p.program_group.code and '[' + _p.program_group.code + '] '
                 or '', _p.program_group.name_short and
                 _p.program_group.name_short or _p.program_group.name or ''),
                None, cell_style_value),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        c_specs = [
            ('program_title', 1, 0, 'text', _('Program'), None,
                cell_style_title),
            ('program_value', 1, 0, 'text',
                '%s%s' %
                (_p.program.code and '[' + _p.program.code + '] ' or '',
                 _p.program.name_short and _p.program.name_short or
                 _p.program.name or ''), None, cell_style_value),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        c_specs = [
            ('project_group_title', 1, 0, 'text', _('Project Group'), None,
                cell_style_title),
            ('project_group_value', 1, 0, 'text',
                '%s%s' %
                (_p.project_group.code and '[' + _p.project_group.code + '] '
                 or '', _p.project_group.name_short and
                 _p.project_group.name_short or _p.project_group.name or ''),
                None, cell_style_value),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        c_specs = [
            ('project_title', 1, 0, 'text', _('Project'), None,
                cell_style_title),
            ('project_value', 1, 0, 'text',
                '%s%s' %
                (_p.project.code and '[' + _p.project.code + '] ' or '',
                 _p.project.name_short and _p.project.name_short or
                 _p.project.name or ''), None, cell_style_value),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        c_specs = [
            ('export_date_title', 1, 0, 'text', _('Export Date'), None,
                cell_style_title),
            ('export_date_value', 1, 0, 'text',
                datetime.datetime.now().strftime('%d-%m-%Y'), None,
                cell_style_value)
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        c_specs = [
            ('responsible_by_title', 1, 0, 'text', _('Responsible by'), None,
                cell_style_title),
            ('responsible_by_value', 1, 0, 'text', user.name, None,
                cell_style_value),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        c_sizes = self.column_sizes
        c_specs = [('empty%s' % i, 1, c_sizes[i], 'text', None)
                   for i in range(0, len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, set_column_size=True)

        # Column Header
        cell_style = xlwt.easyxf(
            _xs['bold'] + _xs['center'] + _xs['borders_all'] +
            "pattern: pattern solid, fore_color ice_blue;")
        c_specs = [
            ('project', 1, 0, 'text', _('Project'), None, cell_style),
            ('name', 1, 0, 'text', _('Project Name'),
                None, cell_style),
            ('c_or_n', 1, 0, 'text', _('C/N'), None, cell_style),
            ('functional_area', 1, 0, 'text', _('Functional Area'),
                None, cell_style),
            ('program', 1, 0, 'text', _('Program'), None, cell_style),
            ('project_group', 1, 0, 'text', _('Project Group'),
                None, cell_style),
            ('nstda_strategy', 1, 0, 'text', _('NSTDA Strategy'),
                None, cell_style),
            ('project_objective', 1, 0, 'text', _('Objective'),
                None, cell_style),
            ('section_program', 1, 0, 'text', _('Section Program'),
                None, cell_style),
            ('mission', 1, 0, 'text', _('Mission'), None, cell_style),
            ('project_kind', 1, 0, 'text', _('Project Kind'),
                None, cell_style),
            ('project_type', 1, 0, 'text', _('Project Type'),
                None, cell_style),
            ('org', 1, 0, 'text', _('Org'), None, cell_style),
            ('costcenter', 1, 0, 'text', _('Costcenter'), None, cell_style),
            ('owner_division', 1, 0, 'text', _('Owner Division'),
                None, cell_style),
            ('pm_employee', 1, 0, 'text', _('Project Manager'),
                None, cell_style),
            ('budget_method', 1, 0, 'text', _('Budget Method'),
                None, cell_style),
            ('date_start', 1, 0, 'text', _('Start Date'), None, cell_style),
            ('date_end', 1, 0, 'text', _('End Date'), None, cell_style),
            ('project_duration', 1, 0, 'text', _('Duration'),
                None, cell_style),
            ('project_status', 1, 0, 'text', _('Project Status'),
                None, cell_style),
            ('analyst_employee', 1, 0, 'text', _('Project Analyst'),
                None, cell_style),
            ('ref_program', 1, 0, 'text', _('Program Reference'),
                None, cell_style),
            ('external_fund_type', 1, 0, 'text', _('External Fund Type'),
                None, cell_style),
            ('external_fund_name', 1, 0, 'text', _('External Fund Name'),
                None, cell_style),
            ('priority', 1, 0, 'text', _('Priority'), None, cell_style),
            ('fy1', 1, 0, 'text', _('FY1'), None, cell_style),
            ('fy2', 1, 0, 'text', _('FY2'), None, cell_style),
            ('fy3', 1, 0, 'text', _('FY3'), None, cell_style),
            ('fy4', 1, 0, 'text', _('FY4'), None, cell_style),
            ('fy5', 1, 0, 'text', _('FY5'), None, cell_style),
            ('revenue_budget', 1, 0, 'text', _('Revenue Budget'),
                None, cell_style),
            ('overall_revenue_plan', 1, 0, 'text', _('Overall Revenue Plan'),
                None, cell_style),
            ('pfm_publications', 1, 0, 'text', _('Publication'),
                None, cell_style),
            ('pfm_patents', 1, 0, 'text', _('Patent'), None, cell_style),
            ('pfm_petty_patents', 1, 0, 'text', _('Petty Patent'),
                None, cell_style),
            ('pfm_copyrights', 1, 0, 'text', _('Copy Right'),
                None, cell_style),
            ('pfm_trademarks', 1, 0, 'text', _('Trademark'), None, cell_style),
            ('pfm_plant_varieties', 1, 0, 'text', _('Plant Varieties'),
                None, cell_style),
            ('pfm_laboratory_prototypes', 1, 0, 'text',
                _('Laboratory Prototype'), None, cell_style),
            ('pfm_field_prototypes', 1, 0, 'text', _('Field Prototype'),
                None, cell_style),
            ('pfm_commercial_prototypes', 1, 0, 'text',
                _('Commercial Prototype'), None, cell_style),
            ('overall_revenue', 1, 0, 'text', _('Accum. Revenue'),
                None, cell_style),
            ('current_revenue', 1, 0, 'text',
                _('Current Year Revenue'), None, cell_style),
            ('overall_expense_budget', 1, 0, 'text',
                _('Overall Expense Budget'), None, cell_style),
            ('overall_actual', 1, 0, 'text', _('Accum. Expense'),
                None, cell_style),
            ('overall_commit', 1, 0, 'text', _('Accum. Commitment'),
                None, cell_style),
            ('overall_expense_balance', 1, 0, 'text',
                _('Remaining Expense Budget'), None, cell_style),
            ('planned', 1, 0, 'text', _('Current Budget'),
                None, cell_style),
            ('released', 1, 0, 'text', _('Current Released'),
                None, cell_style),
            ('all_commit', 1, 0, 'text', _('Current All Commit'),
                None, cell_style),
            ('actual', 1, 0, 'text', _('Current Actual'),
                None, cell_style),
            ('balance', 1, 0, 'text', _('Remaining Budget'),
                None, cell_style),
            ('est_commit', 1, 0, 'text', _('Estimated Commitment'),
                None, cell_style),
            ('m1', 1, 0, 'text', _('Oct'), None, cell_style),
            ('m2', 1, 0, 'text', _('Nov'), None, cell_style),
            ('m3', 1, 0, 'text', _('Dec'), None, cell_style),
            ('m4', 1, 0, 'text', _('Jan'), None, cell_style),
            ('m5', 1, 0, 'text', _('Feb'), None, cell_style),
            ('m6', 1, 0, 'text', _('Mar'), None, cell_style),
            ('m7', 1, 0, 'text', _('Apr'), None, cell_style),
            ('m8', 1, 0, 'text', _('May'), None, cell_style),
            ('m9', 1, 0, 'text', _('Jun'), None, cell_style),
            ('m10', 1, 0, 'text', _('Jul'), None, cell_style),
            ('m11', 1, 0, 'text', _('Aug'), None, cell_style),
            ('m12', 1, 0, 'text', _('Sep'), None, cell_style),
            ('planned_amount', 1, 0, 'text', _('Planned Amount'),
                None, cell_style),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        row_start = row_pos

        # Column Detail
        cell_format = _xs['borders_all']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_integer = xlwt.easyxf(
            cell_format + _xs['right'])
        cell_style_decimal = xlwt.easyxf(
            cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)
        for line in _p.report:
            c_specs = [
                ('project', 1, 0, 'text',
                    '%s%s' %
                    (line.project_id.code and
                     '[' + line.project_id.code + '] ' or '',
                     line.project_id.name_short and line.project_id.name_short
                     or line.project_id.name or ''), None, cell_style),
                ('name', 1, 0, 'text', line.name, None, cell_style),
                ('c_or_n', 1, 0, 'text', C_OR_N.get(line.c_or_n, None),
                    None, cell_style),
                ('functional_area', 1, 0, 'text',
                    '%s%s' %
                    (line.functional_area_id.code and
                     '[' + line.functional_area_id.code + '] ' or '',
                     line.functional_area_id.name_short and
                     line.functional_area_id.name_short or
                     line.functional_area_id.name or ''), None, cell_style),
                ('program', 1, 0, 'text',
                    '%s%s' %
                    (line.program_id.code and
                     '[' + line.program_id.code + '] ' or '',
                     line.program_id.name_short and line.program_id.name_short
                     or line.program_id.name or ''), None, cell_style),
                ('project_group', 1, 0, 'text',
                    '%s%s' %
                    (line.project_group_id.code and
                     '[' + line.project_group_id.code + '] ' or '',
                     line.project_group_id.name_short and
                     line.project_group_id.name_short or
                     line.project_group_id.name or ''), None, cell_style),
                ('nstda_strategy', 1, 0, 'text',
                    '%s%s' %
                    (line.nstda_strategy_id.code and
                     '[' + line.nstda_strategy_id.code + '] ' or '',
                     line.nstda_strategy_id.name_short and
                     line.nstda_strategy_id.name_short or
                     line.nstda_strategy_id.name or ''), None, cell_style),
                ('project_objective', 1, 0, 'text',
                    line.project_objective, None, cell_style),
                ('section_program', 1, 0, 'text',
                    '%s%s' %
                    (line.section_program_id.code and
                     '[' + line.section_program_id.code + '] ' or '',
                     line.section_program_id.name_short and
                     line.section_program_id.name_short or
                     line.section_program_id.name or ''), None, cell_style),
                ('mission', 1, 0, 'text', line.mission_id.name,
                    None, cell_style),
                ('project_kind', 1, 0, 'text',
                    PROJECT_KIND.get(line.project_kind, None), None,
                    cell_style),
                ('project_type', 1, 0, 'text', line.project_type, None,
                    cell_style),
                ('org', 1, 0, 'text',
                    '%s%s' %
                    (line.org_id.code and '[' + line.org_id.code + '] ' or '',
                     line.org_id.name_short and line.org_id.name_short or
                     line.org_id.name or ''), None, cell_style),
                ('costcenter', 1, 0, 'text',
                    '%s%s' %
                    (line.costcenter_id.code and
                     '[' + line.costcenter_id.code + '] ' or '',
                     line.costcenter_id.name_short and
                     line.costcenter_id.name_short or line.costcenter_id.name
                     or ''), None, cell_style),
                ('owner_division', 1, 0, 'text',
                    '%s%s' %
                    (line.owner_division_id.code and
                     '[' + line.owner_division_id.code + '] ' or '',
                     line.owner_division_id.name_short and
                     line.owner_division_id.name_short or
                     line.owner_division_id.name or ''), None, cell_style),
                ('pm_employee', 1, 0, 'text', line.pm_employee_id.name,
                    None, cell_style),
                ('budget_method', 1, 0, 'text',
                    BUDGET_METHOD.get(line.budget_method, None),
                    None, cell_style),
                ('date_start', 1, 0, 'text', line.date_start,
                    None, cell_style),
                ('date_end', 1, 0, 'text', line.date_end, None, cell_style),
                ('project_duration', 1, 0, 'number', line.project_duration,
                    None, cell_style_integer),
                ('project_status', 1, 0, 'text', line.project_status,
                    None, cell_style),
                ('analyst_employee', 1, 0, 'text',
                    line.analyst_employee_id.name, None, cell_style),
                ('ref_program', 1, 0, 'text',
                    '%s%s' %
                    (line.ref_program_id.code and
                     '[' + line.ref_program_id.code + '] ' or '',
                     line.ref_program_id.name_short and
                     line.ref_program_id.name_short and
                     line.ref_program_id.name or ''), None, cell_style),
                ('external_fund_type', 1, 0, 'text',
                    EXTERNAL_FUND_TYPE.get(line.external_fund_type, None),
                    None, cell_style),
                ('external_fund_name', 1, 0, 'text', line.external_fund_name,
                    None, cell_style),
                ('priority', 1, 0, 'text', line.priority, None, cell_style),
                ('fy1', 1, 0, 'number', line.fy1, None, cell_style_decimal),
                ('fy2', 1, 0, 'number', line.fy2, None, cell_style_decimal),
                ('fy3', 1, 0, 'number', line.fy3, None, cell_style_decimal),
                ('fy4', 1, 0, 'number', line.fy4, None, cell_style_decimal),
                ('fy5', 1, 0, 'number', line.fy5, None, cell_style_decimal),
                ('revenue_budget', 1, 0, 'number', line.revenue_budget,
                    None, cell_style_decimal),
                ('overall_revenue_plan', 1, 0, 'number',
                    line.overall_revenue_plan, None, cell_style_decimal),
                ('pfm_publications', 1, 0, 'number', line.pfm_publications,
                    None, cell_style_integer),
                ('pfm_patents', 1, 0, 'number', line.pfm_patents,
                    None, cell_style_integer),
                ('pfm_petty_patents', 1, 0, 'number', line.pfm_petty_patents,
                    None, cell_style_integer),
                ('pfm_copyrights', 1, 0, 'number', line.pfm_copyrights,
                    None, cell_style_integer),
                ('pfm_trademarks', 1, 0, 'number', line.pfm_trademarks,
                    None, cell_style_integer),
                ('pfm_plant_varieties', 1, 0, 'number',
                    line.pfm_plant_varieties, None, cell_style_integer),
                ('pfm_laboratory_prototypes', 1, 0, 'number',
                    line.pfm_laboratory_prototypes, None, cell_style_integer),
                ('pfm_field_prototypes', 1, 0, 'number',
                    line.pfm_field_prototypes, None, cell_style_integer),
                ('pfm_commercial_prototypes', 1, 0, 'number',
                    line.pfm_commercial_prototypes, None, cell_style_integer),
                ('overall_revenue', 1, 0, 'number', line.overall_revenue,
                    None, cell_style_decimal),
                ('current_revenue', 1, 0, 'number', line.current_revenue,
                    None, cell_style_decimal),
                ('overall_expense_budget', 1, 0, 'number',
                    line.overall_expense_budget, None, cell_style_decimal),
                ('overall_actual', 1, 0, 'number', line.overall_actual,
                    None, cell_style_decimal),
                ('overall_commit', 1, 0, 'number', line.overall_commit,
                    None, cell_style_decimal),
                ('overall_expense_balance', 1, 0, 'number',
                    line.overall_expense_balance, None, cell_style_decimal),
                ('planned', 1, 0, 'number', line.planned,
                    None, cell_style_decimal),
                ('released', 1, 0, 'number', line.released,
                    None, cell_style_decimal),
                ('all_commit', 1, 0, 'number', line.all_commit,
                    None, cell_style_decimal),
                ('actual', 1, 0, 'number', line.actual,
                    None, cell_style_decimal),
                ('balance', 1, 0, 'number', line.balance,
                    None, cell_style_decimal),
                ('est_commit', 1, 0, 'number', line.est_commit,
                    None, cell_style_decimal),
                ('m1', 1, 0, 'number', line.m1, None, cell_style_decimal),
                ('m2', 1, 0, 'number', line.m2, None, cell_style_decimal),
                ('m3', 1, 0, 'number', line.m3, None, cell_style_decimal),
                ('m4', 1, 0, 'number', line.m4, None, cell_style_decimal),
                ('m5', 1, 0, 'number', line.m5, None, cell_style_decimal),
                ('m6', 1, 0, 'number', line.m6, None, cell_style_decimal),
                ('m7', 1, 0, 'number', line.m7, None, cell_style_decimal),
                ('m8', 1, 0, 'number', line.m8, None, cell_style_decimal),
                ('m9', 1, 0, 'number', line.m9, None, cell_style_decimal),
                ('m10', 1, 0, 'number', line.m10, None, cell_style_decimal),
                ('m11', 1, 0, 'number', line.m11, None, cell_style_decimal),
                ('m12', 1, 0, 'number', line.m12, None, cell_style_decimal),
                ('planned_amount', 1, 0, 'number', line.planned_amount,
                    None, cell_style_decimal),
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)

        # Column Footer
        cell_format = _xs['borders_all'] + _xs['bold']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_total = xlwt.easyxf(
            cell_format + "pattern: pattern solid, fore_color ice_blue;")
        cell_style_decimal = xlwt.easyxf(
            cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)
        fy1_start = rowcol_to_cell(row_start, 26)
        fy1_end = rowcol_to_cell(row_pos - 1, 26)
        fy1_formula = 'SUM(' + fy1_start + ':' + fy1_end + ')'
        fy2_start = rowcol_to_cell(row_start, 27)
        fy2_end = rowcol_to_cell(row_pos - 1, 27)
        fy2_formula = 'SUM(' + fy2_start + ':' + fy2_end + ')'
        fy3_start = rowcol_to_cell(row_start, 28)
        fy3_end = rowcol_to_cell(row_pos - 1, 28)
        fy3_formula = 'SUM(' + fy3_start + ':' + fy3_end + ')'
        fy4_start = rowcol_to_cell(row_start, 29)
        fy4_end = rowcol_to_cell(row_pos - 1, 29)
        fy4_formula = 'SUM(' + fy4_start + ':' + fy4_end + ')'
        fy5_start = rowcol_to_cell(row_start, 30)
        fy5_end = rowcol_to_cell(row_pos - 1, 30)
        fy5_formula = 'SUM(' + fy5_start + ':' + fy5_end + ')'
        revenue_budget_start = rowcol_to_cell(row_start, 31)
        revenue_budget_end = rowcol_to_cell(row_pos - 1, 31)
        revenue_budget_formula = \
            'SUM(' + revenue_budget_start + ':' + revenue_budget_end + ')'
        overall_revenue_plan_start = rowcol_to_cell(row_start, 32)
        overall_revenue_plan_end = rowcol_to_cell(row_pos - 1, 32)
        overall_revenue_plan_formula = \
            'SUM(' + overall_revenue_plan_start + ':' + \
            overall_revenue_plan_end + ')'
        overall_revenue_start = rowcol_to_cell(row_start, 42)
        overall_revenue_end = rowcol_to_cell(row_pos - 1, 42)
        overall_revenue_formula = \
            'SUM(' + overall_revenue_start + ':' + overall_revenue_end + ')'
        current_revenue_start = rowcol_to_cell(row_start, 43)
        current_revenue_end = rowcol_to_cell(row_pos - 1, 43)
        current_revenue_formula = \
            'SUM(' + current_revenue_start + ':' + current_revenue_end + ')'
        overall_expense_budget_start = rowcol_to_cell(row_start, 44)
        overall_expense_budget_end = rowcol_to_cell(row_pos - 1, 44)
        overall_expense_budget_formula = \
            'SUM(' + overall_expense_budget_start + ':' + \
            overall_expense_budget_end + ')'
        overall_actual_start = rowcol_to_cell(row_start, 45)
        overall_actual_end = rowcol_to_cell(row_pos - 1, 45)
        overall_actual_formula = \
            'SUM(' + overall_actual_start + ':' + overall_actual_end + ')'
        overall_commit_start = rowcol_to_cell(row_start, 46)
        overall_commit_end = rowcol_to_cell(row_pos - 1, 46)
        overall_commit_formula = \
            'SUM(' + overall_commit_start + ':' + overall_commit_end + ')'
        overall_expense_balance_start = rowcol_to_cell(row_start, 47)
        overall_expense_balance_end = rowcol_to_cell(row_pos - 1, 47)
        overall_expense_balance_formula = \
            'SUM(' + overall_expense_balance_start + ':' + \
            overall_expense_balance_end + ')'
        planned_start = rowcol_to_cell(row_start, 48)
        planned_end = rowcol_to_cell(row_pos - 1, 48)
        planned_formula = 'SUM(' + planned_start + ':' + planned_end + ')'
        released_start = rowcol_to_cell(row_start, 49)
        released_end = rowcol_to_cell(row_pos - 1, 49)
        released_formula = 'SUM(' + released_start + ':' + released_end + ')'
        all_commit_start = rowcol_to_cell(row_start, 50)
        all_commit_end = rowcol_to_cell(row_pos - 1, 50)
        all_commit_formula = \
            'SUM(' + all_commit_start + ':' + all_commit_end + ')'
        actual_start = rowcol_to_cell(row_start, 51)
        actual_end = rowcol_to_cell(row_pos - 1, 51)
        actual_formula = 'SUM(' + actual_start + ':' + actual_end + ')'
        balance_start = rowcol_to_cell(row_start, 52)
        balance_end = rowcol_to_cell(row_pos - 1, 52)
        balance_formula = 'SUM(' + balance_start + ':' + balance_end + ')'
        est_commit_start = rowcol_to_cell(row_start, 53)
        est_commit_end = rowcol_to_cell(row_pos - 1, 53)
        est_formula = 'SUM(' + est_commit_start + ':' + est_commit_end + ')'
        m1_start = rowcol_to_cell(row_start, 54)
        m1_end = rowcol_to_cell(row_pos - 1, 54)
        m1_formula = 'SUM(' + m1_start + ':' + m1_end + ')'
        m2_start = rowcol_to_cell(row_start, 55)
        m2_end = rowcol_to_cell(row_pos - 1, 55)
        m2_formula = 'SUM(' + m2_start + ':' + m2_end + ')'
        m3_start = rowcol_to_cell(row_start, 56)
        m3_end = rowcol_to_cell(row_pos - 1, 56)
        m3_formula = 'SUM(' + m3_start + ':' + m3_end + ')'
        m4_start = rowcol_to_cell(row_start, 57)
        m4_end = rowcol_to_cell(row_pos - 1, 57)
        m4_formula = 'SUM(' + m4_start + ':' + m4_end + ')'
        m5_start = rowcol_to_cell(row_start, 58)
        m5_end = rowcol_to_cell(row_pos - 1, 58)
        m5_formula = 'SUM(' + m5_start + ':' + m5_end + ')'
        m6_start = rowcol_to_cell(row_start, 59)
        m6_end = rowcol_to_cell(row_pos - 1, 59)
        m6_formula = 'SUM(' + m6_start + ':' + m6_end + ')'
        m7_start = rowcol_to_cell(row_start, 60)
        m7_end = rowcol_to_cell(row_pos - 1, 60)
        m7_formula = 'SUM(' + m7_start + ':' + m7_end + ')'
        m8_start = rowcol_to_cell(row_start, 61)
        m8_end = rowcol_to_cell(row_pos - 1, 61)
        m8_formula = 'SUM(' + m8_start + ':' + m8_end + ')'
        m9_start = rowcol_to_cell(row_start, 62)
        m9_end = rowcol_to_cell(row_pos - 1, 62)
        m9_formula = 'SUM(' + m9_start + ':' + m9_end + ')'
        m10_start = rowcol_to_cell(row_start, 63)
        m10_end = rowcol_to_cell(row_pos - 1, 63)
        m10_formula = 'SUM(' + m10_start + ':' + m10_end + ')'
        m11_start = rowcol_to_cell(row_start, 64)
        m11_end = rowcol_to_cell(row_pos - 1, 64)
        m11_formula = 'SUM(' + m11_start + ':' + m11_end + ')'
        m12_start = rowcol_to_cell(row_start, 65)
        m12_end = rowcol_to_cell(row_pos - 1, 65)
        m12_formula = 'SUM(' + m12_start + ':' + m12_end + ')'
        planned_amount_start = rowcol_to_cell(row_start, 66)
        planned_amount_end = rowcol_to_cell(row_pos - 1, 66)
        planned_amount_formula = \
            'SUM(' + planned_amount_start + ':' + planned_amount_end + ')'
        c_specs = [
            ('project', 1, 0, 'text', None, None, cell_style),
            ('name', 1, 0, 'text', None, None, cell_style),
            ('c_or_n', 1, 0, 'text', None, None, cell_style),
            ('functional_area', 1, 0, 'text', None, None, cell_style),
            ('program', 1, 0, 'text', None, None, cell_style),
            ('project_group', 1, 0, 'text', None, None, cell_style),
            ('nstda_strategy', 1, 0, 'text', None, None, cell_style),
            ('project_objective', 1, 0, 'text', None, None, cell_style),
            ('section_program', 1, 0, 'text', None, None, cell_style),
            ('mission', 1, 0, 'text', None, None, cell_style),
            ('project_kind', 1, 0, 'text', None, None, cell_style),
            ('project_type', 1, 0, 'text', None, None, cell_style),
            ('org', 1, 0, 'text', None, None, cell_style),
            ('costcenter', 1, 0, 'text', None, None, cell_style),
            ('owner_division', 1, 0, 'text', None, None, cell_style),
            ('pm_employee', 1, 0, 'text', None, None, cell_style),
            ('budget_method', 1, 0, 'text', None, None, cell_style),
            ('date_start', 1, 0, 'text', None, None, cell_style),
            ('date_end', 1, 0, 'text', None, None, cell_style),
            ('project_duration', 1, 0, 'number', None,
                None, cell_style_integer),
            ('project_status', 1, 0, 'text', None, None, cell_style),
            ('analyst_employee', 1, 0, 'text', None, None, cell_style),
            ('ref_program', 1, 0, 'text', None, None, cell_style),
            ('external_fund_type', 1, 0, 'text', None, None, cell_style),
            ('external_fund_name', 1, 0, 'text', None, None, cell_style),
            ('priority', 1, 0, 'text', _('Total'), None, cell_style_total),
            ('fy1', 1, 0, 'number', None, fy1_formula, cell_style_decimal),
            ('fy2', 1, 0, 'number', None, fy2_formula, cell_style_decimal),
            ('fy3', 1, 0, 'number', None, fy3_formula, cell_style_decimal),
            ('fy4', 1, 0, 'number', None, fy4_formula, cell_style_decimal),
            ('fy5', 1, 0, 'number', None, fy5_formula, cell_style_decimal),
            ('revenue_budget', 1, 0, 'number', None, revenue_budget_formula,
                cell_style_decimal),
            ('overall_revenue_plan', 1, 0, 'number', None,
                overall_revenue_plan_formula, cell_style_decimal),
            ('pfm_publications', 1, 0, 'text', None, None, cell_style),
            ('pfm_patents', 1, 0, 'text', None, None, cell_style),
            ('pfm_petty_patents', 1, 0, 'text', None, None, cell_style),
            ('pfm_copyrights', 1, 0, 'text', None, None, cell_style),
            ('pfm_trademarks', 1, 0, 'text', None, None, cell_style),
            ('pfm_plant_varieties', 1, 0, 'text', None, None, cell_style),
            ('pfm_laboratory_prototypes', 1, 0, 'text', None,
                None, cell_style),
            ('pfm_field_prototypes', 1, 0, 'text', None, None, cell_style),
            ('pfm_commercial_prototypes', 1, 0, 'text', None,
                None, cell_style),
            ('overall_revenue', 1, 0, 'number', None, overall_revenue_formula,
                cell_style_decimal),
            ('current_revenue', 1, 0, 'number', None, current_revenue_formula,
                cell_style_decimal),
            ('overall_expense_budget', 1, 0, 'number', None,
                overall_expense_budget_formula, cell_style_decimal),
            ('overall_actual', 1, 0, 'number', None, overall_actual_formula,
                cell_style_decimal),
            ('overall_commit', 1, 0, 'number', None, overall_commit_formula,
                cell_style_decimal),
            ('overall_expense_balance', 1, 0, 'number', None,
                overall_expense_balance_formula, cell_style_decimal),
            ('planned', 1, 0, 'number', None, planned_formula,
                cell_style_decimal),
            ('released', 1, 0, 'number', None, released_formula,
                cell_style_decimal),
            ('all_commit', 1, 0, 'number', None, all_commit_formula,
                cell_style_decimal),
            ('actual', 1, 0, 'number', None, actual_formula,
                cell_style_decimal),
            ('balance', 1, 0, 'number', None, balance_formula,
                cell_style_decimal),
            ('est_commit', 1, 0, 'number', None, est_formula,
                cell_style_decimal),
            ('m1', 1, 0, 'number', None, m1_formula, cell_style_decimal),
            ('m2', 1, 0, 'number', None, m2_formula, cell_style_decimal),
            ('m3', 1, 0, 'number', None, m3_formula, cell_style_decimal),
            ('m4', 1, 0, 'number', None, m4_formula, cell_style_decimal),
            ('m5', 1, 0, 'number', None, m5_formula, cell_style_decimal),
            ('m6', 1, 0, 'number', None, m6_formula, cell_style_decimal),
            ('m7', 1, 0, 'number', None, m7_formula, cell_style_decimal),
            ('m8', 1, 0, 'number', None, m8_formula, cell_style_decimal),
            ('m9', 1, 0, 'number', None, m9_formula, cell_style_decimal),
            ('m10', 1, 0, 'number', None, m10_formula, cell_style_decimal),
            ('m11', 1, 0, 'number', None, m11_formula, cell_style_decimal),
            ('m12', 1, 0, 'number', None, m12_formula, cell_style_decimal),
            ('planned_amount', 1, 0, 'number', None, planned_amount_formula,
                cell_style_decimal),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)


BudgetPlanProjectAnalysisReportXLS(
    'report.budget_plan_project_analysis_report_xls',
    'budget.plan.project.line',
    parser=BudgetPlanProjectAnalysisReportXLSParser)
