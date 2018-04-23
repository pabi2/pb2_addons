# -*- coding: utf-8 -*
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell
from openerp.report import report_sxw
from openerp.tools.translate import _
import xlwt
import datetime

CHARGE_TYPE = {
    'internal': 'Internal',
    'external': 'External',
}

BUDGET_METHOD = {
    'revenue': 'Revenue',
    'expense': 'Expense',
}

COLUMN_SIZES = [
    ('org', 25),
    ('sector', 25),
    ('sub_sector', 25),
    ('division', 25),
    ('section', 25),
    ('section_program', 25),
    ('budget_method', 25),
    ('charge_type', 25),
    ('activity_group', 25),
    ('job_order', 25),
    ('description', 25),
    ('reason', 25),
    ('unit', 25),
    ('unit_price', 25),
    ('activity_unit', 25),
    ('total_budget', 25),
    ('previous_year_commitment', 25),
    ('oct', 25),
    ('nov', 25),
    ('dec', 25),
    ('jan', 25),
    ('feb', 25),
    ('mar', 25),
    ('apr', 25),
    ('may', 25),
    ('jun', 25),
    ('jul', 25),
    ('aug', 25),
    ('sep', 25),
    ('total_of_phased_entries', 25),
    ('total_minus_phased_total', 25),
    ('check_total_minus_phased_total', 25)
]


class BudgetPlanUnitAnalysisReportXLSParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(BudgetPlanUnitAnalysisReportXLSParser, self).__init__(
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
        org_id = form.get('org_id', False)
        sector_id = form.get('sector_id', False)
        subsector_id = form.get('subsector_id', False)
        division_id = form.get('division_id', False)
        section_id = form.get('section_id', False)
        budget_method = form.get('budget_method', False)

        # Browse Fiscalyear
        Fiscalyear = self.pool.get('account.fiscalyear')
        fiscalyear = Fiscalyear.browse(cr, uid, fiscalyear_id)

        # Browse Structure
        Org = self.pool.get('res.org')
        Sector = self.pool.get('res.sector')
        Subsector = self.pool.get('res.subsector')
        Division = self.pool.get('res.division')
        Section = self.pool.get('res.section')
        org = Org.browse(cr, uid, org_id)
        sector = Sector.browse(cr, uid, sector_id)
        subsector = Subsector.browse(cr, uid, subsector_id)
        division = Division.browse(cr, uid, division_id)
        section = Section.browse(cr, uid, section_id)

        # Browse Report
        Report = self.pool.get('budget.plan.unit.line')
        domain = [('fiscalyear_id', '=', fiscalyear_id),
                  ('state', 'not in', ('1_draft', '4_cancel', '5_reject'))]
        if org:
            domain += [('org_id', '=', org_id)]
        if sector:
            domain += [('sector_id', '=', sector_id)]
        if subsector:
            domain += [('subsector_id', '=', subsector_id)]
        if division:
            domain += [('division_id', '=', division_id)]
        if section:
            domain += [('section_id', '=', section_id)]
        if budget_method:
            domain += [('budget_method', '=', budget_method)]
        report_ids = Report.search(cr, uid, domain)
        report = Report.browse(cr, uid, report_ids)

        # Update Context
        self.localcontext.update({
            'fiscalyear': fiscalyear,
            'org': org,
            'sector': sector,
            'subsector': subsector,
            'division': division,
            'section': section,
            'budget_method': budget_method,
            'report': report,
        })

        return super(BudgetPlanUnitAnalysisReportXLSParser, self).set_context(
            objects, data, report_ids, report_type=report_type)


class BudgetPlanUnitAnalysisReportXLS(report_xls):
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
            ('org_title', 1, 0, 'text', _('Org'), None, cell_style_title),
            ('org_value', 1, 0, 'text',
                '%s%s' %
                (_p.org.code and '[' + _p.org.code + '] ' or '',
                 _p.org.name_short and _p.org.name_short or _p.org.name or ''),
             None, cell_style_value)
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        c_specs = [
            ('sector_title', 1, 0, 'text', _('Sector'), None,
                cell_style_title),
            ('sector_value', 1, 0, 'text',
                '%s%s' %
                (_p.sector.code and '[' + _p.sector.code + '] ' or '',
                 _p.sector.name_short and _p.sector.name_short or
                 _p.sector.name or ''), None, cell_style_value),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        c_specs = [
            ('sub_sector_title', 1, 0, 'text', _('Sub Sector'), None,
                cell_style_title),
            ('sub_sector_value', 1, 0, 'text',
                '%s%s' %
                (_p.subsector.code and '[' + _p.subsector.code + '] ' or '',
                 _p.subsector.name_short and _p.subsector.name_short or
                 _p.subsector.name or ''), None, cell_style_value),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        c_specs = [
            ('division_title', 1, 0, 'text', _('Division'), None,
                cell_style_title),
            ('division_value', 1, 0, 'text',
                '%s%s' %
                (_p.division.code and '[' + _p.division.code + '] ' or '',
                 _p.division.name_short and _p.division.name_short or
                 _p.division.name or ''), None, cell_style_value),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        c_specs = [
            ('section_title', 1, 0, 'text', _('Section'), None,
                cell_style_title),
            ('section_value', 1, 0, 'text',
                '%s%s' %
                (_p.section.code and '[' + _p.section.code + '] ' or '',
                 _p.section.name_short and _p.section.name_short or
                 _p.section.name or ''), None, cell_style_value),
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
            ('org', 1, 0, 'text', _('Org'), None, cell_style),
            ('sector', 1, 0, 'text', _('Sector'), None, cell_style),
            ('sub_sector', 1, 0, 'text', _('Sub Sector'), None, cell_style),
            ('division', 1, 0, 'text', _('Division'), None, cell_style),
            ('section', 1, 0, 'text', _('Section'), None, cell_style),
            ('section_program', 1, 0, 'text', _('Section Program'),
                None, cell_style),
            ('budget_method', 1, 0, 'text', _('Budget Method'),
                None, cell_style),
            ('charge_type', 1, 0, 'text', _('Charge Type'), None, cell_style),
            ('activity_group', 1, 0, 'text', ('Activity Group'), None,
                cell_style),
            ('job_order', 1, 0, 'text', _('Job Order'), None, cell_style),
            ('description', 1, 0, 'text', _('Description'), None, cell_style),
            ('reason', 1, 0, 'text', _('Reason'), None, cell_style),
            ('unit', 1, 0, 'text', _('Unit'), None, cell_style),
            ('unit_price', 1, 0, 'text', _('Unit Price'), None, cell_style),
            ('activity_unit', 1, 0, 'text', _('Activity Unit'), None,
                cell_style),
            ('total_budget', 1, 0, 'text', _('Total Budget'), None,
                cell_style),
            ('previous_year_commitment', 1, 0, 'text',
                _('Previous Year Commitment'), None, cell_style),
            ('oct', 1, 0, 'text', _('Oct'), None, cell_style),
            ('nov', 1, 0, 'text', _('Nov'), None, cell_style),
            ('dec', 1, 0, 'text', _('Dec'), None, cell_style),
            ('jan', 1, 0, 'text', _('Jan'), None, cell_style),
            ('feb', 1, 0, 'text', _('Feb'), None, cell_style),
            ('mar', 1, 0, 'text', _('Mar'), None, cell_style),
            ('apr', 1, 0, 'text', _('Apr'), None, cell_style),
            ('may', 1, 0, 'text', _('May'), None, cell_style),
            ('jun', 1, 0, 'text', _('Jun'), None, cell_style),
            ('jul', 1, 0, 'text', _('Jul'), None, cell_style),
            ('aug', 1, 0, 'text', _('Aug'), None, cell_style),
            ('sep', 1, 0, 'text', _('Sep'), None, cell_style),
            ('total_of_phased_entries', 1, 0, 'text',
                _('Total of phased entries'), None, cell_style),
            ('total_minus_phased_total', 1, 0, 'text',
                _('Total minus phased total'), None, cell_style),
            ('check_total_minus_phased_total', 1, 0, 'text', None, None,
                xlwt.easyxf(_xs['borders_all'] + _xs['fill_blue']))
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        row_start = row_pos

        # Column Detail
        cell_format = _xs['borders_all']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_decimal = xlwt.easyxf(
            cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)
        for line in _p.report:
            total_budget_formula = \
                rowcol_to_cell(row_pos, 12) + '*' + \
                rowcol_to_cell(row_pos, 13) + '*' + rowcol_to_cell(row_pos, 14)
            total_of_phased_entries_start = rowcol_to_cell(row_pos, 17)
            total_of_phased_entries_end = rowcol_to_cell(row_pos, 28)
            total_of_phased_entries_formula = \
                'SUM(' + total_of_phased_entries_start + ':' + \
                total_of_phased_entries_end + ')'
            total_minus_phased_total_formula = \
                'IF(' + rowcol_to_cell(row_pos, 15) + '-' + \
                rowcol_to_cell(row_pos, 29) + '<>0,' + \
                rowcol_to_cell(row_pos, 15) + '-' + \
                rowcol_to_cell(row_pos, 29) + ',0)'
            check_total_minus_phased_total_formula = \
                'IF(ABS(' + rowcol_to_cell(row_pos, 30) + ')>0,"Error","")'
            c_specs = [
                ('org', 1, 0, 'text',
                    '%s%s' %
                    (line.org_id.code and '[' + line.org_id.code + '] ' or '',
                     line.org_id.name_short and line.org_id.name_short or
                     line.org_id.name or ''), None, cell_style),
                ('sector', 1, 0, 'text',
                    '%s%s' %
                    (line.sector_id.code and
                     '[' + line.sector_id.code + '] ' or '',
                     line.sector_id.name_short and line.sector_id.name_short or
                     line.sector_id.name or ''), None, cell_style),
                ('sub_sector', 1, 0, 'text',
                    '%s%s' %
                    (line.subsector_id.code and
                     '[' + line.subsector_id.code + '] ' or '',
                     line.subsector_id.name_short and
                     line.subsector_id.name_short or
                     line.subsector_id.name or ''), None, cell_style),
                ('division', 1, 0, 'text',
                    '%s%s' %
                    (line.division_id.code and
                     '[' + line.division_id.code + '] ' or '',
                     line.division_id.name_short and
                     line.division_id.name_short or
                     line.division_id.name or ''), None, cell_style),
                ('section', 1, 0, 'text',
                    '%s%s' %
                    (line.section_id.code and
                     '[' + line.section_id.code + '] ' or '',
                     line.section_id.name_short and
                     line.section_id.name_short or line.section_id.name or ''),
                    None, cell_style),
                ('section_program', 1, 0, 'text',
                    '%s%s' %
                    (line.section_program_id.code and
                     '[' + line.section_program_id.code + '] ' or '',
                     line.section_program_id.name_short and
                     line.section_program_id.name_short or
                     line.section_program_id.name or ''), None, cell_style),
                ('budget_method', 1, 0, 'text',
                    BUDGET_METHOD.get(line.budget_method, None), None,
                    cell_style),
                ('charge_type', 1, 0, 'text',
                    CHARGE_TYPE.get(line.charge_type, None), None, cell_style),
                ('activity_group', 1, 0, 'text', line.activity_group_id.name,
                    None, cell_style),
                ('job_order', 1, 0, 'text', line.cost_control_name or None,
                    None, cell_style),
                ('description', 1, 0, 'text', line.description or None, None,
                    cell_style),
                ('reason', 1, 0, 'text', line.reason or None, None,
                    cell_style),
                ('unit', 1, 0, 'number', line.unit, None, cell_style_decimal),
                ('unit_price', 1, 0, 'number', line.activity_unit_price, None,
                    cell_style_decimal),
                ('activity_unit', 1, 0, 'number', line.activity_unit, None,
                    cell_style_decimal),
                ('total_budget', 1, 0, 'number', None, total_budget_formula,
                    cell_style_decimal),
                ('previous_year_commitment', 1, 0, 'number', line.m0, None,
                    cell_style_decimal),
                ('oct', 1, 0, 'number', line.m1, None, cell_style_decimal),
                ('nov', 1, 0, 'number', line.m2, None, cell_style_decimal),
                ('dec', 1, 0, 'number', line.m3, None, cell_style_decimal),
                ('jan', 1, 0, 'number', line.m4, None, cell_style_decimal),
                ('feb', 1, 0, 'number', line.m5, None, cell_style_decimal),
                ('mar', 1, 0, 'number', line.m6, None, cell_style_decimal),
                ('apr', 1, 0, 'number', line.m7, None, cell_style_decimal),
                ('may', 1, 0, 'number', line.m8, None, cell_style_decimal),
                ('jun', 1, 0, 'number', line.m9, None, cell_style_decimal),
                ('jul', 1, 0, 'number', line.m10, None, cell_style_decimal),
                ('aug', 1, 0, 'number', line.m11, None, cell_style_decimal),
                ('sep', 1, 0, 'number', line.m12, None, cell_style_decimal),
                ('total_of_phased_entries', 1, 0, 'number', None,
                    total_of_phased_entries_formula, cell_style_decimal),
                ('total_minus_phased_total', 1, 0, 'number', None,
                    total_minus_phased_total_formula, cell_style_decimal),
                ('check_total_minus_phased_total', 1, 0, 'text', None,
                    check_total_minus_phased_total_formula, cell_style),
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
        total_budget_start = rowcol_to_cell(row_start, 15)
        total_budget_end = rowcol_to_cell(row_pos - 1, 15)
        total_budget_formula = \
            'SUM(' + total_budget_start + ':' + total_budget_end + ')'
        previous_year_commitment_start = rowcol_to_cell(row_start, 16)
        previous_year_commitment_end = rowcol_to_cell(row_pos - 1, 16)
        previous_year_commitment_formula = \
            'SUM(' + previous_year_commitment_start + ':' + \
            previous_year_commitment_end + ')'
        oct_start = rowcol_to_cell(row_start, 17)
        oct_end = rowcol_to_cell(row_pos - 1, 17)
        oct_formula = 'SUM(' + oct_start + ':' + oct_end + ')'
        nov_start = rowcol_to_cell(row_start, 18)
        nov_end = rowcol_to_cell(row_pos - 1, 18)
        nov_formula = 'SUM(' + nov_start + ':' + nov_end + ')'
        dec_start = rowcol_to_cell(row_start, 19)
        dec_end = rowcol_to_cell(row_pos - 1, 19)
        dec_formula = 'SUM(' + dec_start + ':' + dec_end + ')'
        jan_start = rowcol_to_cell(row_start, 20)
        jan_end = rowcol_to_cell(row_pos - 1, 20)
        jan_formula = 'SUM(' + jan_start + ':' + jan_end + ')'
        feb_start = rowcol_to_cell(row_start, 21)
        feb_end = rowcol_to_cell(row_pos - 1, 21)
        feb_formula = 'SUM(' + feb_start + ':' + feb_end + ')'
        mar_start = rowcol_to_cell(row_start, 22)
        mar_end = rowcol_to_cell(row_pos - 1, 22)
        mar_formula = 'SUM(' + mar_start + ':' + mar_end + ')'
        apr_start = rowcol_to_cell(row_start, 23)
        apr_end = rowcol_to_cell(row_pos - 1, 23)
        apr_formula = 'SUM(' + apr_start + ':' + apr_end + ')'
        may_start = rowcol_to_cell(row_start, 24)
        may_end = rowcol_to_cell(row_pos - 1, 24)
        may_formula = 'SUM(' + may_start + ':' + may_end + ')'
        jun_start = rowcol_to_cell(row_start, 25)
        jun_end = rowcol_to_cell(row_pos - 1, 25)
        jun_formula = 'SUM(' + jun_start + ':' + jun_end + ')'
        jul_start = rowcol_to_cell(row_start, 26)
        jul_end = rowcol_to_cell(row_pos - 1, 26)
        jul_formula = 'SUM(' + jul_start + ':' + jul_end + ')'
        aug_start = rowcol_to_cell(row_start, 27)
        aug_end = rowcol_to_cell(row_pos - 1, 27)
        aug_formula = 'SUM(' + aug_start + ':' + aug_end + ')'
        sep_start = rowcol_to_cell(row_start, 28)
        sep_end = rowcol_to_cell(row_pos - 1, 28)
        sep_formula = 'SUM(' + sep_start + ':' + sep_end + ')'
        total_of_phased_entries_start = rowcol_to_cell(row_start, 29)
        total_of_phased_entries_end = rowcol_to_cell(row_pos - 1, 29)
        total_of_phased_entries_formula = \
            'SUM(' + total_of_phased_entries_start + ':' + \
            total_of_phased_entries_end + ')'
        total_minus_phased_total_start = rowcol_to_cell(row_start, 30)
        total_minus_phased_total_end = rowcol_to_cell(row_pos - 1, 30)
        total_minus_phased_total_formula = \
            'SUM(' + total_minus_phased_total_start + ':' + \
            total_minus_phased_total_end + ')'
        check_total_minus_phased_total_formula = \
            'IF(ABS(' + rowcol_to_cell(row_pos, 30) + ')>0,"Error","")'
        c_specs = [
            ('org', 1, 0, 'text', None, None, cell_style),
            ('sector', 1, 0, 'text', None, None, cell_style),
            ('sub_sector', 1, 0, 'text', None, None, cell_style),
            ('division', 1, 0, 'text', None, None, cell_style),
            ('section', 1, 0, 'text', None, None, cell_style),
            ('section_program', 1, 0, 'text', None, None, cell_style),
            ('budget_method', 1, 0, 'text', None, None, cell_style),
            ('charge_type', 1, 0, 'text', None, None, cell_style),
            ('activity_group', 1, 0, 'text', None, None, cell_style),
            ('job_order', 1, 0, 'text', None, None, cell_style),
            ('description', 1, 0, 'text', None, None, cell_style),
            ('reason', 1, 0, 'text', None, None, cell_style),
            ('unit', 1, 0, 'text', None, None, cell_style),
            ('unit_price', 1, 0, 'text', None, None, cell_style),
            ('activity_unit', 1, 0, 'text', _('Total'), None,
                cell_style_total),
            ('total_budget', 1, 0, 'number', None, total_budget_formula,
                cell_style_decimal),
            ('previous_year_commitment', 1, 0, 'number', None,
                previous_year_commitment_formula, cell_style_decimal),
            ('oct', 1, 0, 'number', None, oct_formula, cell_style_decimal),
            ('nov', 1, 0, 'number', None, nov_formula, cell_style_decimal),
            ('dec', 1, 0, 'number', None, dec_formula, cell_style_decimal),
            ('jan', 1, 0, 'number', None, jan_formula, cell_style_decimal),
            ('feb', 1, 0, 'number', None, feb_formula, cell_style_decimal),
            ('mar', 1, 0, 'number', None, mar_formula, cell_style_decimal),
            ('apr', 1, 0, 'number', None, apr_formula, cell_style_decimal),
            ('may', 1, 0, 'number', None, may_formula, cell_style_decimal),
            ('jun', 1, 0, 'number', None, jun_formula, cell_style_decimal),
            ('jul', 1, 0, 'number', None, jul_formula, cell_style_decimal),
            ('aug', 1, 0, 'number', None, aug_formula, cell_style_decimal),
            ('sep', 1, 0, 'number', None, sep_formula, cell_style_decimal),
            ('total_of_phased_entries', 1, 0, 'number', None,
                total_of_phased_entries_formula, cell_style_decimal),
            ('total_minus_phased_total', 1, 0, 'number', None,
                total_minus_phased_total_formula, cell_style_decimal),
            ('check_total_minus_phased_total', 1, 0, 'text', None,
                check_total_minus_phased_total_formula, cell_style)
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)


BudgetPlanUnitAnalysisReportXLS(
    'report.budget_plan_unit_analysis_report_xls',
    'budget.plan.unit.line',
    parser=BudgetPlanUnitAnalysisReportXLSParser)
