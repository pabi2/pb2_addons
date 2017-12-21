# -*- coding: utf-8 -*
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell
from openerp.tools.translate import _
import xlwt

CHART_VIEW = {
    'res_personnel_costcenter': 'Personnel',
    'res_invest_asset': 'Investment Asset',
    'res_section': 'Unit Based',
    'res_project': 'Project Based',
    'res_invest_construction': 'Investment Construction',
}

COLUMN_SIZES = [
    ('budget_structure', 20),
    ('budget_code', 20),
    ('budget_name', 40),
    ('budget_control', 20),
    ('budget_release', 20),
    ('expense_commitment', 20),
    ('pr_commitment', 20),
    ('po_commitment', 20),
    ('total_commitment', 20),
    ('actual', 20),
    ('consumed_budget', 20),
    ('residual_budget', 20),
    ('percent_consumed_budget', 20),
]


class BudgetCostCentreReportXLSParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(BudgetCostCentreReportXLSParser, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'report_name': _('Budgeting Report by Cost Centre'),
        })

    def set_context(self, objects, data, ids, report_type=None):
        # Declare Valiable
        cr, uid = self.cr, self.uid

        # Get Data
        form = data.get('form', {})
        period_id = form.get('period_id', False)
        costcenter_id = form.get('costcenter_id', False)

        # Browse Period
        Period = self.pool.get('account.period')
        period = Period.browse(cr, uid, period_id)

        # Browse Cost Center
        CostCenter = self.pool.get('res.costcenter')
        costcenter = CostCenter.browse(cr, uid, costcenter_id)

        # Browse Report
        Report = self.pool.get('budget.cost.centre.report')
        report_ids = Report.search(
            cr, uid, [('date_stop', '<=', period.date_stop),
                      ('costcenter_id', '=', costcenter_id)])
        report = Report.browse(cr, uid, report_ids)

        # Update Context
        self.localcontext.update({
            'period': period,
            'costcenter': costcenter,
            'report': report,
        })

        return super(BudgetCostCentreReportXLSParser, self).set_context(
            objects, data, report_ids, report_type=report_type)


class BudgetCostCentreReportXLS(report_xls):
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
            ('report_name', 1, 0, 'text', _p.report_name),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)
        c_specs = [
            ('period_end_title', 1, 0, 'text', _('For the period ended'), None,
                cell_style),
            ('period_end_value', 1, 0, 'text', _p.period.name),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        c_specs = [
            ('costcenter_title', 1, 0, 'text', _('Cost Center'), None,
                cell_style),
            ('costcenter_value', 1, 0, 'text', _p.costcenter.code),
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
            ('budget_code', 1, 0, 'text', _('Budget Code'), None, cell_style),
            ('budget_name', 1, 0, 'text', _('Budget Name'), None, cell_style),
            ('budget_control', 1, 0, 'text', _('Budget Control'), None,
                cell_style),
            ('budget_release', 1, 0, 'text', _('Budget Release'), None,
                cell_style),
            ('expense_commitment', 1, 0, 'text', _('EX'), None, cell_style),
            ('pr_commitment', 1, 0, 'text', _('PR'), None, cell_style),
            ('po_commitment', 1, 0, 'text', _('PO'), None, cell_style),
            ('total_commitment', 1, 0, 'text', _('Total Commitment'), None,
                cell_style),
            ('actual', 1, 0, 'text', _('Actual'), None, cell_style),
            ('consumed_budget', 1, 0, 'text', _('Consumed Budget'), None,
                cell_style),
            ('residual_budget', 1, 0, 'text', _('Residual Budget'), None,
                cell_style),
            ('percent_consumed_budget', 1, 0, 'text', _('% Consumed Budget'),
                None, cell_style),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)

        # Column Detail
        row_pos_subtotal_list = []
        cell_format = _xs['right'] + _xs['borders_all']
        cell_style = xlwt.easyxf(_xs['borders_all'])
        cell_style_decimal = xlwt.easyxf(
            cell_format, num_format_str=report_xls.decimal_format)
        cell_style_percent = xlwt.easyxf(cell_format, num_format_str='0.00%')
        cell_format = _xs['right'] + _xs['borders_all'] + _xs['bold']
        cell_style_subtotal = xlwt.easyxf(cell_format + _xs['fill'])
        cell_style_subtotal_decimal = xlwt.easyxf(
            cell_format, num_format_str=report_xls.decimal_format)
        cell_style_subtotal_percent = xlwt.easyxf(
            cell_format, num_format_str='0.00%')
        for sequence in range(1, 6):
            row_start = row_pos
            report = _p.report.filtered(lambda l: l.sequence == sequence)
            for line in report.mapped('budget_id'):
                budget_report = report.filtered(
                    lambda l: l.budget_id._table == line._table and
                    l.budget_id.id == line.id)
                chart_view = CHART_VIEW.get(line._table, False)
                total_commitment_start = rowcol_to_cell(row_pos, 5)
                total_commitment_end = rowcol_to_cell(row_pos, 7)
                total_commitment_formula = \
                    'SUM(' + total_commitment_start + ':' + \
                    total_commitment_end + ')'
                consumed_budget_start = rowcol_to_cell(row_pos, 8)
                consumed_budget_end = rowcol_to_cell(row_pos, 9)
                consumed_budget_formula = \
                    'SUM(' + consumed_budget_start + ':' + \
                    consumed_budget_end + ')'
                residual_budget_formula = \
                    rowcol_to_cell(row_pos, 4) + '-' + \
                    rowcol_to_cell(row_pos, 10)
                percent_consumed_formula = \
                    rowcol_to_cell(row_pos, 10) + '/' + \
                    rowcol_to_cell(row_pos, 4)
                c_specs = [
                    ('budget_structure', 1, 0, 'text', chart_view, None,
                        cell_style),
                    ('budget_code', 1, 0, 'text', line.code, None, cell_style),
                    ('budget_name', 1, 0, 'text', line.name, None, cell_style),
                    ('budget_control', 1, 0, 'number',
                        sum(budget_report.mapped('planned_amount')), None,
                        cell_style_decimal),
                    ('budget_release', 1, 0, 'number',
                        sum(budget_report.mapped('released_amount')), None,
                        cell_style_decimal),
                    ('expense_commitment', 1, 0, 'number',
                        sum(budget_report.mapped('amount_exp_commit')), None,
                        cell_style_decimal),
                    ('pr_commitment', 1, 0, 'number',
                        sum(budget_report.mapped('amount_pr_commit')), None,
                        cell_style_decimal),
                    ('po_commitment', 1, 0, 'number',
                        sum(budget_report.mapped('amount_po_commit')), None,
                        cell_style_decimal),
                    ('total_commitment', 1, 0, 'number', None,
                        total_commitment_formula, cell_style_decimal),
                    ('actual', 1, 0, 'number',
                        sum(budget_report.mapped('amount_actual')), None,
                        cell_style_decimal),
                    ('consumed_budget', 1, 0, 'number', None,
                        consumed_budget_formula, cell_style_decimal),
                    ('residual_budget', 1, 0, 'number', None,
                        residual_budget_formula, cell_style_decimal),
                    ('percent_consumed_budget', 1, 0, 'number', None,
                        percent_consumed_formula, cell_style_percent)
                ]
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(ws, row_pos, row_data)

            if report:
                budget_control_start = rowcol_to_cell(row_start, 3)
                budget_control_end = rowcol_to_cell(row_pos - 1, 3)
                budget_control_formula = \
                    'SUM(' + budget_control_start + ':' + \
                    budget_control_end + ')'
                budget_release_start = rowcol_to_cell(row_start, 4)
                budget_release_end = rowcol_to_cell(row_pos - 1, 4)
                budget_release_formula = \
                    'SUM(' + budget_release_start + ':' + \
                    budget_release_end + ')'
                expense_commitment_start = rowcol_to_cell(row_start, 5)
                expense_commitment_end = rowcol_to_cell(row_pos - 1, 5)
                expense_commitment_formula = \
                    'SUM(' + expense_commitment_start + ':' + \
                    expense_commitment_end + ')'
                pr_commitment_start = rowcol_to_cell(row_start, 6)
                pr_commitment_end = rowcol_to_cell(row_pos - 1, 6)
                pr_commitment_formula = \
                    'SUM(' + pr_commitment_start + ':' + \
                    pr_commitment_end + ')'
                po_commitment_start = rowcol_to_cell(row_start, 7)
                po_commitment_end = rowcol_to_cell(row_pos - 1, 7)
                po_commitment_formula = \
                    'SUM(' + po_commitment_start + ':' + \
                    po_commitment_end + ')'
                total_commitment_start = rowcol_to_cell(row_pos, 5)
                total_commitment_end = rowcol_to_cell(row_pos, 7)
                total_commitment_formula = \
                    'SUM(' + total_commitment_start + ':' + \
                    total_commitment_end + ')'
                actual_start = rowcol_to_cell(row_start, 9)
                actual_end = rowcol_to_cell(row_pos - 1, 9)
                actual_formula = 'SUM(' + actual_start + ':' + actual_end + ')'
                consumed_budget_start = rowcol_to_cell(row_pos, 8)
                consumed_budget_end = rowcol_to_cell(row_pos, 9)
                consumed_budget_formula = \
                    'SUM(' + consumed_budget_start + ':' + \
                    consumed_budget_end + ')'
                residual_budget_formula = \
                    rowcol_to_cell(row_pos, 4) + '-' + \
                    rowcol_to_cell(row_pos, 10)
                percent_consumed_budget_formula = \
                    rowcol_to_cell(row_pos, 10) + '/' + \
                    rowcol_to_cell(row_pos, 4)
                c_specs = [
                    ('budget_structure', 1, 0, 'text', None),
                    ('budget_code', 1, 0, 'text', None),
                    ('budget_name', 1, 0, 'text', _('Total ') + chart_view,
                        None, cell_style_subtotal),
                    ('budget_control', 1, 0, 'number', None,
                        budget_control_formula, cell_style_subtotal_decimal),
                    ('budget_release', 1, 0, 'number', None,
                        budget_release_formula, cell_style_subtotal_decimal),
                    ('expense_commitment', 1, 0, 'number', None,
                        expense_commitment_formula,
                        cell_style_subtotal_decimal),
                    ('pr_commitment', 1, 0, 'number', None,
                        pr_commitment_formula, cell_style_subtotal_decimal),
                    ('po_commitment', 1, 0, 'number', None,
                        po_commitment_formula, cell_style_subtotal_decimal),
                    ('total_commitment', 1, 0, 'number', None,
                        total_commitment_formula, cell_style_subtotal_decimal),
                    ('actual', 1, 0, 'number', None, actual_formula,
                        cell_style_subtotal_decimal),
                    ('consumed_budget', 1, 0, 'number', None,
                        consumed_budget_formula, cell_style_subtotal_decimal),
                    ('residual_budget', 1, 0, 'number', None,
                        residual_budget_formula, cell_style_subtotal_decimal),
                    ('percent_consumed_budget', 1, 0, 'number', None,
                        percent_consumed_budget_formula,
                        cell_style_subtotal_percent)
                ]
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(ws, row_pos, row_data)
                row_pos_subtotal_list.append(row_pos)

        # Column Footer
        cell_format = _xs['bold'] + _xs['borders_all'] + _xs['fill']
        cell_style_total = xlwt.easyxf(cell_format)
        cell_style_total_decimal = xlwt.easyxf(
            cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)
        cell_style_total_percent = xlwt.easyxf(
            cell_format + _xs['right'], num_format_str='0.00%')
        budget_control_formula_list = []
        budget_release_formula_list = []
        expense_commitment_formula_list = []
        pr_commitment_formula_list = []
        po_commitment_formula_list = []
        actual_formula_list = []
        for row_pos_subtotal in row_pos_subtotal_list:
            budget_control_formula_list.append(
                rowcol_to_cell(row_pos_subtotal - 1, 3))
            budget_release_formula_list.append(
                rowcol_to_cell(row_pos_subtotal - 1, 4))
            expense_commitment_formula_list.append(
                rowcol_to_cell(row_pos_subtotal - 1, 5))
            pr_commitment_formula_list.append(
                rowcol_to_cell(row_pos_subtotal - 1, 6))
            po_commitment_formula_list.append(
                rowcol_to_cell(row_pos_subtotal - 1, 7))
            actual_formula_list.append(rowcol_to_cell(row_pos_subtotal - 1, 9))
        if row_pos_subtotal_list:
            budget_control_formula = '+'.join(budget_control_formula_list)
            budget_release_formula = '+'.join(budget_release_formula_list)
            expense_commitment_formula = \
                '+'.join(expense_commitment_formula_list)
            pr_commitment_formula = '+'.join(pr_commitment_formula_list)
            po_commitment_formula = '+'.join(po_commitment_formula_list)
            actual_formula = '+'.join(actual_formula_list)
        else:
            budget_control_formula = '0'
            budget_release_formula = '0'
            expense_commitment_formula = '0'
            pr_commitment_formula = '0'
            po_commitment_formula = '0'
            actual_formula = '0'
        total_commitment_start = rowcol_to_cell(row_pos, 5)
        total_commitment_end = rowcol_to_cell(row_pos, 7)
        total_commitment_formula = \
            'SUM(' + total_commitment_start + ':' + total_commitment_end + ')'
        consumed_budget_start = rowcol_to_cell(row_pos, 8)
        consumed_budget_end = rowcol_to_cell(row_pos, 9)
        consumed_budget_formula = \
            'SUM(' + consumed_budget_start + ':' + consumed_budget_end + ')'
        residual_budget_formula = \
            rowcol_to_cell(row_pos, 4) + '-' + rowcol_to_cell(row_pos, 10)
        percent_consumed_budget_formula = \
            rowcol_to_cell(row_pos, 10) + '/' + rowcol_to_cell(row_pos, 4)
        c_specs = [
            ('budget_structure', 1, 0, 'text', _('Grand Total'), None,
                cell_style_total),
            ('budget_code', 1, 0, 'text', None, None, cell_style_total),
            ('budget_name', 1, 0, 'text', None, None, cell_style_total),
            ('budget_control', 1, 0, 'number', None, budget_control_formula,
                cell_style_total_decimal),
            ('budget_release', 1, 0, 'number', None, budget_release_formula,
                cell_style_total_decimal),
            ('expense_commitment', 1, 0, 'number', None,
                expense_commitment_formula, cell_style_total_decimal),
            ('pr_commitment', 1, 0, 'number', None, pr_commitment_formula,
                cell_style_total_decimal),
            ('po_commitment', 1, 0, 'number', None, po_commitment_formula,
                cell_style_total_decimal),
            ('total_commitment', 1, 0, 'number', None,
                total_commitment_formula, cell_style_total_decimal),
            ('actual', 1, 0, 'number', None, actual_formula,
                cell_style_total_decimal),
            ('consumed_budget', 1, 0, 'number', None, consumed_budget_formula,
                cell_style_total_decimal),
            ('residual_budget', 1, 0, 'number', None, residual_budget_formula,
                cell_style_total_decimal),
            ('percent_consumed_budget', 1, 0, 'number', None,
                percent_consumed_budget_formula, cell_style_total_percent)
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)


BudgetCostCentreReportXLS(
    'report.budget_cost_centre_report_xls',
    'budget.monitor.report',
    parser=BudgetCostCentreReportXLSParser)
