# -*- coding: utf-8 -*
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell
from openerp.report import report_sxw
from openerp.tools.translate import _
import xlwt
import datetime
from dateutil import relativedelta

CHART_VIEW = {
    'personnel': 'Personnel',
    'invest_asset': 'Investment Asset',
    'unit_base': 'Unit Based',
    'project_base': 'Project Based',
    'invest_construction': 'Investment Construction',
}

COLUMN_SIZES = [
    ('budget_structure', 25),
    ('budget_plan', 20),
    ('budget_policy', 20),
    ('release_budget', 20),
    ('pr_commitment', 20),
    ('po_commitment', 20),
    ('ex_commitment', 20),
    ('actual', 25),
    ('residual_budget', 20),
    ('percent_actual', 20),
    ('percent_commitment', 20),
    ('total_commitment', 20),
]


class BudgetSummaryReportXLSParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(BudgetSummaryReportXLSParser, self).__init__(cr, uid, name,
                                                           context=context)
        self.localcontext.update({
            'report_name': _('Budget Summary Report'),
        })

    def set_context(self, objects, data, ids, report_type=None):
        # Declare Valiable
        cr, uid = self.cr, self.uid

        # Get Data
        fiscalyear_id = data.get('form', {}).get('fiscalyear_id', False)

        # Browse Fiscalyear
        Fiscalyear = self.pool.get('account.fiscalyear')
        fiscalyear = Fiscalyear.browse(cr, uid, fiscalyear_id)

        # Browse Report
        Report = self.pool.get('budget.summary.report')
        report_ids = Report.search(cr, uid, [('fiscalyear_id', '=',
                                              fiscalyear_id)])
        report = Report.browse(cr, uid, report_ids)

        # Update Context
        self.localcontext.update({
            'fiscalyear': fiscalyear,
            'report': report,
        })

        return super(BudgetSummaryReportXLSParser, self).set_context(
            objects, data, report_ids, report_type=report_type)


class BudgetSummaryReportXLS(report_xls):
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
        cell_style = xlwt.easyxf(_xs['bold'])
        c_specs = [
            ('organization', 1, 0, 'text', _('NSTDA')),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)
        c_specs = [
            ('report_name', 1, 0, 'text', _p.report_name),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)
        c_specs = [
            ('fiscalyear_title', 1, 0, 'text', _('Fiscal Year'), None,
                cell_style),
            ('fiscalyear_value', 1, 0, 'text', _p.fiscalyear.name)
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        date_start = datetime.datetime.strptime(_p.fiscalyear.date_start,
                                                "%Y-%m-%d")
        date_stop = datetime.datetime.strptime(_p.fiscalyear.date_stop,
                                               "%Y-%m-%d")
        c_specs = [
            ('duration', 1, 0, 'text', _('From ') +
             date_start.strftime('%d %B %Y') + _(' to ') +
             date_stop.strftime('%d %B %Y') + _(' (') +
             str(relativedelta.relativedelta(date_stop, date_start).months) +
             _(' Months)'))
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
        cell_style = xlwt.easyxf(_xs['bold'] + _xs['center'] + _xs['fill'] +
                                 _xs['borders_all'])
        c_specs = [
            ('budget_structure', 1, 0, 'text', _('Budget Structure'), None,
                cell_style),
            ('budget_plan', 1, 0, 'text', _('Budget Plan'), None, cell_style),
            ('budget_policy', 1, 0, 'text', _('Budget Policy'), None,
                cell_style),
            ('release_budget', 1, 0, 'text', _('Release Budget'), None,
                cell_style),
            ('pr_commitment', 1, 0, 'text', _('PR Commitment'), None,
                cell_style),
            ('po_commitment', 1, 0, 'text', _('PO  Commitment'), None,
                cell_style),
            ('ex_commitment', 1, 0, 'text', _('EX Commitment'), None,
                cell_style),
            ('actual', 1, 0, 'text', _('Actual'), None, cell_style),
            ('residual_budget', 1, 0, 'text', _('Residual Budget (Released)'),
                None, cell_style),
            ('percent_actual', 1, 0, 'text', _('% Actual'), None, cell_style),
            ('percent_commitment', 1, 0, 'text', _('% Commitment'), None,
                cell_style),
            ('total_commitment', 1, 0, 'text', _('Total Commitment'), None,
                cell_style)
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        row_start = row_pos

        # Column Detail
        cell_format = _xs['right'] + _xs['borders_all']
        cell_style_right = xlwt.easyxf(cell_format)
        cell_style_decimal = xlwt.easyxf(
            cell_format, num_format_str=report_xls.decimal_format)
        for report in _p.report:
            chart_view = CHART_VIEW.get(report.chart_view, False)
            c_specs = [
                ('budget_structure', 1, 0, 'text', chart_view),
                ('budget_plan', 1, 0, 'number', report.plan, None,
                    cell_style_decimal),
                ('budget_policy', 1, 0, 'number', report.policy, None,
                    cell_style_decimal),
                ('release_budget', 1, 0, 'number', report.released, None,
                    cell_style_decimal),
                ('pr_commitment', 1, 0, 'number', report.pr_commit, None,
                    cell_style_decimal),
                ('po_commitment', 1, 0, 'number', report.po_commit, None,
                    cell_style_decimal),
                ('ex_commitment', 1, 0, 'number', report.exp_commit, None,
                    cell_style_decimal),
                ('actual', 1, 0, 'number', report.actual_total, None,
                    cell_style_decimal),
                ('residual_budget', 1, 0, 'number', report.balance, None,
                    cell_style_decimal),
                ('percent_actual', 1, 0, 'text',
                    '{:,.2f}'.format(report.actual_percent) + '%', None,
                    cell_style_right),
                ('percent_commitment', 1, 0, 'text',
                    '{:,.2f}'.format(report.commit_percent) + '%',
                    None, cell_style_right),
                ('total_commitment', 1, 0, 'number', report.commit_total, None,
                    cell_style_decimal)
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)

        # Column Footer
        cell_format = _xs['fill'] + _xs['borders_all'] + _xs['bold']
        cell_style_right = xlwt.easyxf(cell_format + _xs['right'])
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        cell_style_decimal = xlwt.easyxf(
            cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)
        cell_style_percent = xlwt.easyxf(
            cell_format + _xs['right'], num_format_str='0.00%')
        plan_start = rowcol_to_cell(row_start, 1)
        plan_end = rowcol_to_cell(row_pos - 1, 1)
        plan_formula = 'SUM(' + plan_start + ':' + plan_end + ')'
        policy_start = rowcol_to_cell(row_start, 2)
        policy_end = rowcol_to_cell(row_pos - 1, 2)
        policy_formula = 'SUM(' + policy_start + ':' + policy_end + ')'
        released_start = rowcol_to_cell(row_start, 3)
        released_end = rowcol_to_cell(row_pos - 1, 3)
        released_formula = 'SUM(' + released_start + ':' + released_end + ')'
        pr_commit_start = rowcol_to_cell(row_start, 4)
        pr_commit_end = rowcol_to_cell(row_pos - 1, 4)
        pr_commit_formula = \
            'SUM(' + pr_commit_start + ':' + pr_commit_end + ')'
        po_commit_start = rowcol_to_cell(row_start, 5)
        po_commit_end = rowcol_to_cell(row_pos - 1, 5)
        po_commit_formula = \
            'SUM(' + po_commit_start + ':' + po_commit_end + ')'
        exp_commit_start = rowcol_to_cell(row_start, 6)
        exp_commit_end = rowcol_to_cell(row_pos - 1, 6)
        exp_commit_formula = \
            'SUM(' + exp_commit_start + ':' + exp_commit_end + ')'
        actual_total_start = rowcol_to_cell(row_start, 7)
        actual_total_end = rowcol_to_cell(row_pos - 1, 7)
        actual_total_formula = \
            'SUM(' + actual_total_start + ':' + actual_total_end + ')'
        balance_start = rowcol_to_cell(row_start, 8)
        balance_end = rowcol_to_cell(row_pos - 1, 8)
        balance_formula = 'SUM(' + balance_start + ':' + balance_end + ')'
        actual_percent_formula = \
            rowcol_to_cell(row_pos, 7) + '/' + rowcol_to_cell(row_pos, 2)
        commit_percent_formula = \
            rowcol_to_cell(row_pos, 11) + '/' + rowcol_to_cell(row_pos, 2)
        commit_total_start = rowcol_to_cell(row_start, 11)
        commit_total_end = rowcol_to_cell(row_pos - 1, 11)
        commit_total_formula = \
            'SUM(' + commit_total_start + ':' + commit_total_end + ')'
        c_specs = [
            ('budget_structure', 1, 0, 'text', _('Total'), None,
                cell_style_center),
            ('budget_plan', 1, 0, 'number', None, plan_formula,
                cell_style_decimal),
            ('budget_policy', 1, 0, 'number', None, policy_formula,
                cell_style_decimal),
            ('release_budget', 1, 0, 'number', None, released_formula,
                cell_style_decimal),
            ('pr_commitment', 1, 0, 'number', None, pr_commit_formula,
                cell_style_decimal),
            ('po_commitment', 1, 0, 'number', None, po_commit_formula,
                cell_style_decimal),
            ('ex_commitment', 1, 0, 'number', None, exp_commit_formula,
                cell_style_decimal),
            ('actual', 1, 0, 'number', None, actual_total_formula,
                cell_style_decimal),
            ('residual_budget', 1, 0, 'number', None, balance_formula,
                cell_style_decimal),
            ('percent_actual', 1, 0, 'number', None, actual_percent_formula,
                cell_style_percent),
            ('percent_commitment', 1, 0, 'number', None,
                commit_percent_formula, cell_style_percent),
            ('total_commitment', 1, 0, 'number', None, commit_total_formula,
                cell_style_decimal)
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        c_specs = [('empty%s' % i, 1, c_sizes[i], 'text', None)
                   for i in range(0, len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, set_column_size=True)

        # Footer
        cell_format = _xs['borders_all'] + _xs['right']
        cell_style = xlwt.easyxf(_xs['borders_all'])
        cell_style_decimal = xlwt.easyxf(
            cell_format, num_format_str=report_xls.decimal_format)
        cell_style_percent = xlwt.easyxf(cell_format, num_format_str='0.00%')
        actual_formula = rowcol_to_cell(row_pos - 2, 7)
        actual_percent_formula = rowcol_to_cell(row_pos, 1) + '/' + \
            rowcol_to_cell(row_pos + 2, 1)
        budget_policy_formula = rowcol_to_cell(row_pos - 2, 2)
        c_specs = [
            ('actual_title', 1, 0, 'text', _('Actual'), None, cell_style),
            ('actual_value', 1, 0, 'number', None, actual_formula,
                cell_style_decimal),
            ('actual_percent', 1, 0, 'number', None, actual_percent_formula,
                cell_style_percent),
            ('space_1', 1, 0, 'text', None),
            ('space_2', 1, 0, 'text', None),
            ('space_3', 1, 0, 'text', None),
            ('space_4', 1, 0, 'text', None),
            ('budget_policy_title', 1, 0, 'text', _('Budget Policy'), None,
                cell_style),
            ('budget_policy_value', 1, 0, 'number', None,
                budget_policy_formula, cell_style_decimal),
            ('budget_policy_percent', 1, 0, 'number', 1, None,
                cell_style_percent)
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        total_commitment_formula = rowcol_to_cell(row_pos - 3, 11)
        total_commitment_percent_formula = \
            rowcol_to_cell(row_pos, 1) + '/' + rowcol_to_cell(row_pos + 1, 1)
        actual_formula = rowcol_to_cell(row_pos - 1, 1)
        actual_percent_formula = \
            rowcol_to_cell(row_pos, 8) + '/' + rowcol_to_cell(row_pos - 1, 8)
        c_specs = [
            ('total_commitment_title', 1, 0, 'text', _('Total Commitment'),
                None, cell_style),
            ('total_commitment_value', 1, 0, 'number', None,
                total_commitment_formula, cell_style_decimal),
            ('total_commitment_percent', 1, 0, 'text', None,
                total_commitment_percent_formula, cell_style_percent),
            ('space_1', 1, 0, 'text', None),
            ('space_2', 1, 0, 'text', None),
            ('space_3', 1, 0, 'text', None),
            ('space_4', 1, 0, 'text', None),
            ('actual_title', 1, 0, 'text', _('Actual'), None, cell_style),
            ('actual_value', 1, 0, 'text', None, actual_formula,
                cell_style_decimal),
            ('actual_percent', 1, 0, 'text', None, actual_percent_formula,
                cell_style_percent)
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        total_actual_commitment_formula_1 = \
            'SUM(' + rowcol_to_cell(row_pos - 2, 1) + ':' + \
            rowcol_to_cell(row_pos - 1, 1) + ')'
        total_actual_commitment_percent_formula_1 = \
            rowcol_to_cell(row_pos, 1) + '/' + rowcol_to_cell(row_pos, 1)
        total_actual_commitment_formula_2 = rowcol_to_cell(row_pos, 1)
        total_actual_commitment_percent_formula_2 = \
            rowcol_to_cell(row_pos, 8) + '/' + rowcol_to_cell(row_pos - 2, 8)
        c_specs = [
            ('total_actual_commitment_title_1', 1, 0, 'text',
                _('Total Actual + Commitment'), None, cell_style),
            ('total_actual_commitment_value_1', 1, 0, 'number', None,
                total_actual_commitment_formula_1, cell_style_decimal),
            ('total_actual_commitment_percent_1', 1, 0, 'number', None,
                total_actual_commitment_percent_formula_1, cell_style_percent),
            ('space_1', 1, 0, 'text', None),
            ('space_2', 1, 0, 'text', None),
            ('space_3', 1, 0, 'text', None),
            ('space_4', 1, 0, 'text', None),
            ('total_actual_commitment_title_2', 1, 0, 'text',
                _('Total Actual + Commitment'), None, cell_style),
            ('total_actual_commitment_value_2', 1, 0, 'number', None,
                total_actual_commitment_formula_2, cell_style_decimal),
            ('total_actual_commitment_percent_2', 1, 0, 'number', None,
                total_actual_commitment_percent_formula_2, cell_style_percent),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        budget_balance_formula = \
            rowcol_to_cell(row_pos - 3, 8) + '-' + \
            rowcol_to_cell(row_pos - 1, 8)
        budget_balance_percent_formula = \
            rowcol_to_cell(row_pos, 8) + '/' + rowcol_to_cell(row_pos - 3, 8)
        c_specs = [
            ('space_1', 1, 0, 'text', None),
            ('space_2', 1, 0, 'text', None),
            ('space_3', 1, 0, 'text', None),
            ('space_4', 1, 0, 'text', None),
            ('space_5', 1, 0, 'text', None),
            ('space_6', 1, 0, 'text', None),
            ('space_7', 1, 0, 'text', None),
            ('budget_balance_title', 1, 0, 'text',
                _('Budget Balance (Policy)'), None, cell_style),
            ('budget_balance_value', 1, 0, 'number', None,
                budget_balance_formula, cell_style_decimal),
            ('budget_balance_percent', 1, 0, 'number', None,
                budget_balance_percent_formula, cell_style_percent)
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)


BudgetSummaryReportXLS(
    'report.budget_summary_report_xls',
    'budget.monitor.report',
    parser=BudgetSummaryReportXLSParser)
