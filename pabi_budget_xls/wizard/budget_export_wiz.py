# -*- coding: utf-8 -*-
import base64
import cStringIO
import openpyxl
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import quote_sheetname
from openpyxl.styles import PatternFill, Border, Side, Protection, Font
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError

SHEET_FORMULAS = {}


class BudgetExportWizard(models.TransientModel):
    _name = 'unit.budget.plan.export'

    @api.model
    def _default_export_committed_budget(self):
        active_ids = self._context.get('active_ids', [])
        lines = len(self.env['budget.plan.unit.summary'].search(
            [('plan_id', 'in', active_ids)])._ids)
        if lines > 0:
            return False
        return True

    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Template Plan',
    )
    editable_lines = fields.Integer(
        string='Additional Budget lines(Non JobOrder)',
        required=True,
        default=50,
    )
    export_committed_budget = fields.Boolean(
        string="Export Committed Budget?",
        default=_default_export_committed_budget,
    )

    @api.model
    def _add_cell_border(self, sheet, row_start, row_end, col_start, col_end):
        if not row_start:
            row_start = 1
        if not col_start:
            col_start = 0
        thin = Side(border_style="thin", color="000000")
        border = Border(top=thin, left=thin, right=thin, bottom=thin)
        row = row_start
        for row in range(row_start, row_end):
            for col in range(col_start, col_end+1):
                sheet.cell(row=row, column=col).border = border

    @api.model
    def _make_cell_editable(self, sheet, row_start, row_end,
                            col_start, col_end, skip_cell):
        if not row_start:
            row_start = 1
        if not col_start:
            col_start = 0
        protection = Protection(locked=False)
        row = row_start
        for row in range(row_start, row_end):
            for col in range(col_start, col_end+1):
                if skip_cell and col == skip_cell:
                    continue
                sheet.cell(row=row, column=col).protection = protection

    @api.model
    def _make_cell_color_filled(self, sheet, row_start, row_end,
                                col_start, col_end, col_list):
        fill_color = 'D3D3D3'
        if self._context.get('color', False):
            fill_color = self._context['color']
        greyFill = PatternFill(
            start_color=fill_color,
            end_color=fill_color,
            fill_type='solid',
        )
        row = row_start
        if not col_list:
            col_list = range(col_start, col_end+1)

        for row in range(row_start, row_end):
            for col in col_list:
                sheet.cell(row=row, column=col).fill = greyFill

    @api.model
    def _update_costcontrol_masterdata(self, workbook):
        costcontrols = self.env['cost.control'].search([])
        ConstControl_MasterSheet = False
        try:
            ConstControl_MasterSheet = \
                workbook.get_sheet_by_name('master_job_order')
        except:
            ConstControl_MasterSheet = \
                workbook.create_sheet('master_job_order')
        ConstControl_MasterSheet.protection.sheet = True

        bold_font = Font(bold=True, name='Arial', size=11)
        # Add cost control header in cost control data sheet
        ConstControl_MasterSheet.cell(row=1,
                                      column=1).value = 'Sequence'
        ConstControl_MasterSheet.cell(row=1,
                                      column=2).value = 'Job Order - English'
        ConstControl_MasterSheet.cell(row=1,
                                      column=3).value = 'Job Order - Thai'
        ConstControl_MasterSheet.cell(row=1,
                                      column=1).font = bold_font
        ConstControl_MasterSheet.cell(row=1,
                                      column=2).font = bold_font
        ConstControl_MasterSheet.cell(row=1,
                                      column=3).font = bold_font
        # Add cost control from odoo in cost control data sheet
        ag_row = 2
        ag_count = 1
        ag_length = 1
        for ag in costcontrols:
            ConstControl_MasterSheet.cell(row=ag_row, column=1, value=ag_count)
            ConstControl_MasterSheet.cell(row=ag_row, column=2, value=ag.name)
            ConstControl_MasterSheet.cell(row=ag_row, column=3, value=ag.name)
            if len(ag.name) > ag_length:
                ag_length = len(ag.name)
            ag_row += 1
            ag_count += 1

        ConstControl_MasterSheet.column_dimensions['A'].width = 11
        ConstControl_MasterSheet.column_dimensions['B'].width = ag_length
        ConstControl_MasterSheet.column_dimensions['C'].width = ag_length

        formula1 = "{0}!$C$2:$C$%s" % (ag_row)
        CostControlList = DataValidation(
            type="list",
            formula1=formula1.format(
                quote_sheetname('master_job_order')
            )
        )
        SHEET_FORMULAS.update({'cost_control_formula': CostControlList})
        return True

    @api.model
    def _update_costcontrol_sheet(self, workbook, budget):
        # center_align = Alignment(horizontal='center')
        # protection = Protection(locked=False)
        ConstControl_Sheet = False
        try:
            ConstControl_Sheet = workbook.get_sheet_by_name('JobOrder')
            # ConstControl_Sheet.protection.sheet = True
        except:
            pass

        # greyFill = PatternFill(
        #     start_color='D3D3D3',
        #     end_color='D3D3D3',
        #     fill_type='solid',
        # )
        # Whitefont = Font(color='FFFFFF')
        if ConstControl_Sheet:
            # Update costcontrol sheet from odoo
            self._update_costcontrol_masterdata(workbook)
            job_order_lines, non_job_order_lines = \
                self._compute_previous_year_amount(budget,
                                                   budget_method='expense')
            ag_list_formula = SHEET_FORMULAS.get('ag_list', False)
            ChargeType = DataValidation(
                type="list",
                formula1='"External,Internal"'
            )
            costcontrol_formula = \
                SHEET_FORMULAS.get('cost_control_formula', False)
            ConstControl_Sheet.add_data_validation(costcontrol_formula)
            ConstControl_Sheet.add_data_validation(ChargeType)
            ConstControl_Sheet.add_data_validation(ag_list_formula)
            org = budget.org_id.code and\
                budget.org_id.code or budget.org_id.name_short
            section = budget.section_id.code and\
                budget.section_id.code or budget.section_id.name_short
            # add header data to sheet
            row = 1
            ConstControl_Sheet.cell(row=row, column=2,
                                    value=budget.fiscalyear_id.name)
            row += 1
            ConstControl_Sheet.cell(row=row, column=2, value=org)
            row += 1
            ConstControl_Sheet.cell(row=row, column=2, value=section)
            row += 1
            ConstControl_Sheet.cell(row=row, column=2,
                                    value=fields.Date.today())
            row += 1
            ConstControl_Sheet.cell(row=row, column=2,
                                    value=self.env.user.name)
            row += 1

            # ag_column_list = []
            cost_cntrl_first_column = 8
            row_gap = 28
            # add job order drop down formula to each job order cell
            for r in range(1, 11):
                costcontrol_formula.add(
                    ConstControl_Sheet.cell(row=cost_cntrl_first_column,
                                            column=2))
                cost_cntrl_first_column = cost_cntrl_first_column + row_gap

            ag_first_column = 13
            row_gap = 8
            for r in range(1, 11):
                # Add charge type and activity 
                # group formula to each job order line
                for rr in range(ag_first_column, ag_first_column+20):
                    ChargeType.add(ConstControl_Sheet.cell(row=rr,
                                                           column=1))
                    ag_list_formula.add(ConstControl_Sheet.cell(row=rr,
                                                                column=2))
                    ag_first_column += 1
                ag_first_column = ag_first_column+row_gap

            cc_f_row = 8
            cc_row_gap = 28
            cc_fi_row = 8
            if job_order_lines:
                # if job order line exists in odoo fill up in excel sheet
                for jb in job_order_lines:
                    line_fi_row = cc_fi_row + 5
                    costcontrol = self.env['cost.control'].browse(jb)
                    ConstControl_Sheet.cell(
                        row=cc_fi_row, column=2).value = costcontrol.name
                    cc_fi_row += cc_row_gap
                    if job_order_lines[jb]:
                        for ag in job_order_lines[jb]:
                            col = 2
                            amt = job_order_lines[jb][ag]
                            if ag:
                                ag_name = \
                                    self.env['account.activity.group'].\
                                    browse(ag).name
                                ConstControl_Sheet.cell(
                                    row=line_fi_row,
                                    column=col).value = ag_name
                            col += 7
                            ConstControl_Sheet.cell(
                                row=line_fi_row, column=col).value = amt
                            line_fi_row += 1
            for const_cntrl_line in budget.cost_control_ids:
                line_f_row = cc_f_row + 5
                if const_cntrl_line.cost_control_id:
                    ConstControl_Sheet.cell(
                        row=cc_f_row, column=2).value = \
                        const_cntrl_line.cost_control_id.name
                    cc_f_row += cc_row_gap
                # add lines in job order sections from job order tab
                if const_cntrl_line.plan_cost_control_line_ids:
                    for line in const_cntrl_line.plan_cost_control_line_ids:
                        col = 1
                        if line.charge_type:
                            if line.charge_type == 'external':
                                ConstControl_Sheet.cell(
                                    row=line_f_row,
                                    column=col).value = 'External'
                            else:
                                ConstControl_Sheet.cell(
                                    row=line_f_row,
                                    column=col).value = 'Internal'
                        col += 1
                        if line.activity_group_id:
                            ConstControl_Sheet.cell(
                                row=line_f_row,
                                column=col).value = line.activity_group_id.name
                        col += 1
                        if line.name:
                            ConstControl_Sheet.cell(
                                row=line_f_row,
                                column=col).value = line.name
                        col += 1
                        col += 1
                        if line.unit:
                            ConstControl_Sheet.cell(
                                row=line_f_row,
                                column=col).value = line.unit
                        col += 1
                        if line.activity_unit_price:
                            ConstControl_Sheet.cell(
                                row=line_f_row,
                                column=col).value = line.activity_unit_price
                        col += 1
                        if line.activity_unit:
                            ConstControl_Sheet.cell(
                                row=line_f_row,
                                column=col).value = line.activity_unit

                        col += 1
                        col += 1
                        col += 1
                        ConstControl_Sheet.cell(
                            row=line_f_row, column=col).value = line.m1
                        col += 1
                        ConstControl_Sheet.cell(
                            row=line_f_row, column=col).value = line.m2
                        col += 1
                        ConstControl_Sheet.cell(
                            row=line_f_row, column=col).value = line.m3
                        col += 1
                        ConstControl_Sheet.cell(
                            row=line_f_row, column=col).value = line.m4
                        col += 1
                        ConstControl_Sheet.cell(
                            row=line_f_row, column=col).value = line.m5
                        col += 1
                        ConstControl_Sheet.cell(
                            row=line_f_row, column=col).value = line.m6
                        col += 1
                        ConstControl_Sheet.cell(
                            row=line_f_row, column=col).value = line.m7
                        col += 1
                        ConstControl_Sheet.cell(
                            row=line_f_row, column=col).value = line.m8
                        col += 1
                        ConstControl_Sheet.cell(
                            row=line_f_row, column=col).value = line.m9
                        col += 1
                        ConstControl_Sheet.cell(
                            row=line_f_row, column=col).value = line.m10
                        col += 1
                        ConstControl_Sheet.cell(
                            row=line_f_row, column=col).value = line.m11
                        col += 1
                        ConstControl_Sheet.cell(
                            row=line_f_row, column=col).value = line.m12
                        col += 3
                        line_f_row += 1
        return True

    @api.model
    def _compute_previous_year_amount(self, budget, budget_method):
        current_fy = budget.fiscalyear_id
        previous_fy = self.env['account.fiscalyear'].search(
            [('date_stop', '<', current_fy.date_start)],
            order='date_stop', limit=1)
        job_order_lines = {}
        non_job_order_lines = {}
        if not self.export_committed_budget or not previous_fy:
            return job_order_lines, non_job_order_lines
        # compute committed amount for previous year 
        if previous_fy:
            report_domain = [('fiscalyear_id', '=', previous_fy.id),
                             ('section_id', '=', budget.section_id.id),
                             ('org_id', '=', budget.org_id.id),
                             ('division_id', '=', budget.division_id.id),
                             ('budget_method', '=', budget_method)]
            report_lines = self.env['budget.monitor.report'].\
                search(report_domain)
            for line in report_lines:
                total_commited_amt =\
                    line.amount_exp_commit +\
                    line.amount_po_commit +\
                    line.amount_pr_commit
                if total_commited_amt == 0.0:
                    continue
                if line.cost_control_id:
                    if line.cost_control_id.id not in job_order_lines:
                        job_order_lines[line.cost_control_id.id] = {}
                    if line.activity_group_id:
                        if line.activity_group_id.id not in \
                                job_order_lines[line.cost_control_id.id]:
                            job_order_lines[line.cost_control_id.id].\
                                update({line.activity_group_id.id:
                                        total_commited_amt})
                        else:
                            cc_id = line.cost_control_id.id
                            ag_id = line.activity_group_id.id
                            job_order_lines[cc_id][ag_id] += total_commited_amt
                    else:
                        if False not in \
                                job_order_lines[line.cost_control_id.id]:
                            job_order_lines[line.cost_control_id.id].\
                                update({False: total_commited_amt})
                        else:
                            cc_id = line.cost_control_id.id
                            job_order_lines[cc_id][False] += total_commited_amt
                else:
                    if line.activity_group_id:
                        if line.activity_group_id.id not in \
                                non_job_order_lines:
                            non_job_order_lines[line.activity_group_id.id] = \
                                total_commited_amt
                        else:
                            non_job_order_lines[line.activity_group_id.id] += \
                                total_commited_amt
                    else:
                        if False not in non_job_order_lines:
                            non_job_order_lines[False] = total_commited_amt
                        else:
                            non_job_order_lines[False] += total_commited_amt
        return job_order_lines, non_job_order_lines

    @api.model
    def _update_non_joborder_sheets(self, Sheet, budget, budget_method):
        # Update lines of Non job order sheets based on odoo budget lines
        NonCostCtrl_Sheet = Sheet
        NonCostCtrl_Sheet.protection.sheet = True
        bold_font = Font(bold=True, name='Arial', size=11)
        ActGroupList = SHEET_FORMULAS.get('ag_list', False)
        ChargeType = SHEET_FORMULAS.get('charge_type', False)
        job_order_lines, non_job_order_lines =\
            self._compute_previous_year_amount(budget, budget_method)
        decimal_type_validation = \
            DataValidation(type="decimal",
                           operator="greaterThanOrEqual",
                           formula1=0)
        NonCostCtrl_Sheet.add_data_validation(decimal_type_validation)
        NonCostCtrl_Sheet.add_data_validation(ActGroupList)
        NonCostCtrl_Sheet.add_data_validation(ChargeType)
        NonCostCtrl_Sheet.cell(row=1, column=5, value=budget.id)
        org = budget.org_id.code and\
            budget.org_id.code or budget.org_id.name_short
        NonCostCtrl_Sheet.cell(row=1, column=2,
                               value=budget.fiscalyear_id.name)
        NonCostCtrl_Sheet.cell(row=2, column=2, value=org)
        NonCostCtrl_Sheet.cell(row=3, column=2,
                               value=budget.section_id.code)
        NonCostCtrl_Sheet.cell(row=4, column=2, value=fields.Date.today())
        NonCostCtrl_Sheet.cell(row=5, column=2, value=self.env.user.name)

        row = 11
        # section_name = budget.section_id.name
        LineStart = row
        if budget_method == 'expense':
            lines = budget.plan_expense_line_ids
        else:
            lines = budget.plan_revenue_line_ids
        if lines:
            for line in lines:
                if line.breakdown_line_id:
                    continue
                ChargeType.add(NonCostCtrl_Sheet.cell(row=row, column=1))
                # Update/create lines in sheet
                if line.charge_type:
                    if line.charge_type == 'external':
                        NonCostCtrl_Sheet.cell(row=row,
                                               column=1).value = 'External'
                    else:
                        NonCostCtrl_Sheet.cell(row=row,
                                               column=1).value = 'Internal'
                ActGroupList.add(NonCostCtrl_Sheet.cell(row=row, column=2))
                ag_name = line.activity_group_id.name
                NonCostCtrl_Sheet.cell(row=row, column=2).value = ag_name
                if line.description:
                    NonCostCtrl_Sheet.cell(
                        row=row, column=3).value = line.description
                NonCostCtrl_Sheet.cell(
                    row=row, column=5).value = line.unit
                NonCostCtrl_Sheet.cell(
                    row=row, column=6).value = line.activity_unit_price
                NonCostCtrl_Sheet.cell(
                    row=row, column=7).value = line.activity_unit

                for cl in range(5, 8):
                    decimal_type_validation.add(
                        NonCostCtrl_Sheet.cell(row=row, column=cl))
                    NonCostCtrl_Sheet.cell(
                        row=row, column=cl).number_format = '#,##0.00'

                NonCostCtrl_Sheet.cell(
                    row=row, column=8).value = \
                    "=E%s*$F$%s*$G$%s" % (row, row, row)
                NonCostCtrl_Sheet.cell(row=row, column=8).number_format = \
                    '#,##0.00'
                NonCostCtrl_Sheet.cell(row=row, column=10).value = line.m1
                NonCostCtrl_Sheet.cell(row=row, column=11).value = line.m2
                NonCostCtrl_Sheet.cell(row=row, column=12).value = line.m3
                NonCostCtrl_Sheet.cell(row=row, column=13).value = line.m4
                NonCostCtrl_Sheet.cell(row=row, column=14).value = line.m5
                NonCostCtrl_Sheet.cell(row=row, column=15).value = line.m6
                NonCostCtrl_Sheet.cell(row=row, column=16).value = line.m7
                NonCostCtrl_Sheet.cell(row=row, column=17).value = line.m8
                NonCostCtrl_Sheet.cell(row=row, column=18).value = line.m9
                NonCostCtrl_Sheet.cell(row=row, column=19).value = line.m10
                NonCostCtrl_Sheet.cell(row=row, column=20).value = line.m11
                NonCostCtrl_Sheet.cell(row=row, column=21).value = line.m12

                for cl in range(5, 22):
                    decimal_type_validation.add(
                        NonCostCtrl_Sheet.cell(row=row, column=cl))
                    NonCostCtrl_Sheet.cell(
                        row=row, column=cl).number_format = '#,##0.00'

                NonCostCtrl_Sheet.cell(
                    row=row, column=22, value="=SUM(J%s:$U$%s)" % (row, row))
                NonCostCtrl_Sheet.cell(
                    row=row, column=23, value="=H%s-$V$%s" % (row, row))
                NonCostCtrl_Sheet.cell(row=row, column=22).number_format = \
                    '#,##0.00'
                NonCostCtrl_Sheet.cell(row=row, column=23).number_format = \
                    '#,##0.00'
                row += 1

        to_row = row + self.editable_lines
        linetofill = row
        for r in range(row, to_row):
            ChargeType.add(NonCostCtrl_Sheet.cell(row=r, column=1))
            ActGroupList.add(NonCostCtrl_Sheet.cell(row=r, column=2))

            for cl in range(5, 8):
                decimal_type_validation.add(
                    NonCostCtrl_Sheet.cell(row=r, column=cl))
                NonCostCtrl_Sheet.cell(
                    row=r, column=cl).number_format = '#,##0.00'
            # Add expression for multiply unit*unit price*activity unit 
            NonCostCtrl_Sheet.cell(
                row=r, column=8).value = "=E%s*$F$%s*$G$%s" % (r, r, r)

            for cl in range(9, 22):
                decimal_type_validation.add(
                    NonCostCtrl_Sheet.cell(row=r, column=cl))
                NonCostCtrl_Sheet.cell(
                    row=r, column=cl).number_format = '#,##0.00'

            # Add expression for get sum of m1 to m12 columns
            NonCostCtrl_Sheet.cell(
                row=r, column=22, value="=SUM(J%s:$U$%s)" % (r, r))
            # Add expression for get difference between total budget
            # and sum of 12 columns
            NonCostCtrl_Sheet.cell(
                row=r, column=23, value="=H%s-$V$%s" % (r, r))

            NonCostCtrl_Sheet.cell(row=r, column=22).number_format = '#,##0.00'
            NonCostCtrl_Sheet.cell(row=r, column=23).number_format = '#,##0.00'

            row += 1
            r += 1
        if non_job_order_lines:
            r = linetofill
            for ag in non_job_order_lines:
                if ag:
                    ActivityGroup = self.env['account.activity.group']
                    ag_name = ActivityGroup.browse(ag).name
                    NonCostCtrl_Sheet.cell(row=r, column=2).value = ag_name
                    NonCostCtrl_Sheet.cell(row=r, column=9).value = \
                        non_job_order_lines[ag]
                else:
                    NonCostCtrl_Sheet.cell(row=r, column=9).value = \
                        non_job_order_lines[ag]
                r += 1

        column_to_fill = [8, 9, 22, 23]
        self._add_cell_border(NonCostCtrl_Sheet,
                              row_start=LineStart,
                              row_end=row,
                              col_start=1,
                              col_end=23)
        self._make_cell_editable(sheet=NonCostCtrl_Sheet,
                                 row_start=LineStart,
                                 row_end=row,
                                 col_start=1,
                                 col_end=21,
                                 skip_cell=8)
        self._make_cell_color_filled(sheet=NonCostCtrl_Sheet,
                                     row_start=LineStart,
                                     row_end=row,
                                     col_start=1,
                                     col_end=1,
                                     col_list=column_to_fill)

        NonCostCtrl_Sheet.cell(row=row, column=7).value = 'Total'
        NonCostCtrl_Sheet.cell(row=row, column=7).font = bold_font
        params = (LineStart, row-1)
        # Add Expression for 
        NonCostCtrl_Sheet.cell(
            row=row, column=8).value = '=SUM(H%s:H%s)' % params
        NonCostCtrl_Sheet.cell(
            row=row, column=9).value = '=SUM(I%s:I%s)' % params
        NonCostCtrl_Sheet.cell(
            row=row, column=10).value = '=SUM(J%s:J%s)' % params
        NonCostCtrl_Sheet.cell(
            row=row, column=11).value = '=SUM(K%s:K%s)' % params
        NonCostCtrl_Sheet.cell(
            row=row, column=12).value = '=SUM(L%s:L%s)' % params
        NonCostCtrl_Sheet.cell(
            row=row, column=13).value = '=SUM(M%s:M%s)' % params
        NonCostCtrl_Sheet.cell(
            row=row, column=14).value = '=SUM(N%s:N%s)' % params
        NonCostCtrl_Sheet.cell(
            row=row, column=15).value = '=SUM(O%s:O%s)' % params
        NonCostCtrl_Sheet.cell(
            row=row, column=16).value = '=SUM(P%s:P%s)' % params
        NonCostCtrl_Sheet.cell(
            row=row, column=17).value = '=SUM(Q%s:Q%s)' % params
        NonCostCtrl_Sheet.cell(
            row=row, column=18).value = '=SUM(R%s:R%s)' % params
        NonCostCtrl_Sheet.cell(
            row=row, column=19).value = '=SUM(S%s:S%s)' % params
        NonCostCtrl_Sheet.cell(
            row=row, column=20).value = '=SUM(T%s:T%s)' % params
        NonCostCtrl_Sheet.cell(
            row=row, column=21).value = '=SUM(U%s:U%s)' % params
        for cl in range(8, 22):
            NonCostCtrl_Sheet.cell(row=row, column=cl).number_format = \
                '#,##0.00'

        NonCostCtrl_Sheet.cell(
            row=6, column=2).value = '=H%s' % (row)

        self._add_cell_border(NonCostCtrl_Sheet, row_start=row,
                              row_end=row+1, col_start=7, col_end=21)
        self._make_cell_color_filled(sheet=NonCostCtrl_Sheet,
                                     row_start=row, row_end=row+1,
                                     col_start=7, col_end=21, col_list=[])

    @api.multi
    def update_budget_xls(self, budget_ids, template_id=None):
        if not template_id:
            raise UserError(_('Please add .xlsx template.'))
        if not budget_ids:
            raise UserError(_('No budget to export.'))
        budgets = self.env['budget.plan.unit'].browse(budget_ids)
        template_file = self.env['ir.attachment'].browse(template_id)

        for budget in budgets:
            exp_file = self.attachment_id.datas.decode('base64')
            stream = cStringIO.StringIO(exp_file)
            workbook = openpyxl.load_workbook(stream)

            try:
                SEC_Sheet = workbook.get_sheet_by_name('master_section')
                SEC_Sheet.protection.sheet = True
            except:
                pass
            try:
                ACM_Sheet = workbook.get_sheet_by_name('master_job_order')
                ACM_Sheet.protection.sheet = True
            except:
                pass
            try:
                ACMc_Sheet = workbook.get_sheet_by_name('c_MasterData')
                ACMc_Sheet.protection.sheet = True
            except:
                pass
            # Add activity group datas in activity group master sheet from odoo
            AG_Sheet = workbook.get_sheet_by_name('master_activity_group')
            AG_Sheet.protection.sheet = True
            activities = self.env['account.activity.group'].search([])

            bold_font = Font(bold=True, name='Arial', size=11)

            # Set header of activity group data sheet
            AG_Sheet.cell(row=1, column=1).value = 'Sequence'
            AG_Sheet.cell(row=1, column=2).value = 'Activity Group - English'
            AG_Sheet.cell(row=1, column=3).value = 'Activity Group - Thai'
            AG_Sheet.cell(row=1, column=1).font = bold_font
            AG_Sheet.cell(row=1, column=2).font = bold_font
            AG_Sheet.cell(row=1, column=3).font = bold_font

            # create lines in activity group data sheet
            ag_row = 2
            ag_count = 1
            ag_length = 1
            for ag in activities:
                AG_Sheet.cell(row=ag_row, column=1, value=ag_count)
                AG_Sheet.cell(row=ag_row, column=2, value=ag.name)
                AG_Sheet.cell(row=ag_row, column=3, value=ag.name)
                if len(ag.name) > ag_length:
                    ag_length = len(ag.name)
                ag_row += 1
                ag_count += 1

            AG_Sheet.column_dimensions['A'].width = 11
            AG_Sheet.column_dimensions['B'].width = ag_length
            AG_Sheet.column_dimensions['C'].width = ag_length

            formula1 = "{0}!$C$2:$C$%s" % (ag_row)
            ActGroupList = DataValidation(
                type="list",
                formula1=formula1.format(
                    quote_sheetname('master_activity_group')
                )
            )
            ChargeType = DataValidation(
                type="list",
                formula1='"External,Internal"'
            )
            # Attach formulas to sheet to use further
            SHEET_FORMULAS.update({'ag_list': ActGroupList})
            SHEET_FORMULAS.update({'charge_type': ChargeType})
            Non_JobOrder_Expense = \
                workbook.get_sheet_by_name('Non_JobOrder_Expense')
            Non_JobOrder_Revenue = \
                workbook.get_sheet_by_name('Non_JobOrder_Revenue')
            self._update_non_joborder_sheets(Non_JobOrder_Expense,
                                             budget,
                                             budget_method='expense')
            self._update_non_joborder_sheets(Non_JobOrder_Revenue,
                                             budget,
                                             budget_method='revenue')
            self._update_costcontrol_sheet(workbook, budget)

            org = budget.org_id.code and\
                budget.org_id.code or budget.org_id.name_short

            stream1 = cStringIO.StringIO()
            workbook.save(stream1)
            filename = '%s-%s-%s-%s.xlsx' % (budget.fiscalyear_id.name,
                                             org,
                                             budget.section_id.code,
                                             template_file.name)
            self.env.cr.execute(""" DELETE FROM budget_xls_output """)
            attachement_id = self.env['ir.attachment'].create({
                'name': filename,
                'datas': stream1.getvalue().encode('base64'),
                'datas_fname': filename,
                'res_model': 'budget.plan.unit',
                'res_id': budget.id,
                'budget_plan_id': budget.id,
                'description': 'Export',
            })
            attach_id = self.env['budget.xls.output'].create({
                'name': filename,
                'xls_output': base64.encodestring(stream1.getvalue()),
            })
            self.env['budget.plan.history'].create({
                'user_id': self.env.user.id,
                'operation_date': fields.Datetime.now(),
                'operation_type': 'export',
                'plan_id': budget.id,
                'attachement_id': attachement_id.id
            })
            return attach_id

    @api.multi
    def export_budget(self):
        budget_ids = self.env.context.get('active_ids')
        attach_id = self.update_budget_xls(budget_ids, self.attachment_id.id)
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'budget.xls.output',
            'res_id': attach_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
