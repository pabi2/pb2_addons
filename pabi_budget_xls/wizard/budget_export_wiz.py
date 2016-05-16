# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import xlrd
import xlwt
import cStringIO
from xlutils.copy import copy
from xlwt.Utils import rowcol_pair_to_cellrange
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class BudgetExportWizard(models.Model):
    _name = 'budget.export.wizard'

    attachment_id = fields.Many2one('ir.attachment', 'Template')

    @api.multi
    def update_budget_xls(self, budget_ids, template_id=None):
        if not template_id:
            raise UserError(_('Please add .xlsx template.'))
        if not budget_ids:
            raise UserError(_('No budget to export.'))
        budgets = self.env['account.budget.prepare'].browse(budget_ids)
        template_file = self.env['ir.attachment'].browse(template_id)

        for budget in budgets:
            editable = xlwt.easyxf('protection: cell_locked false;')
            num_style = xlwt.XFStyle()
            num_style.num_format_str = '_(#,##0.00_);'
            rb = xlrd.open_workbook(
                file_contents=base64.decodestring(template_file.datas),
                formatting_info=True,
            )
            workbook = copy(rb)
            # selected template sheet
            template_sheet = rb.sheet_by_index(0)
            # new budget sheet to export
            budget_sheet = workbook.get_sheet(0)
            budget_sheet.protect = True
            project_detail_row = 0
            project_detail_title = {}
            line_field = False
            # update the budget detail cells like project etc.
            for row in range(template_sheet.nrows):
                for col in range(template_sheet.ncols):
                    title = template_sheet.cell_value(row, col)
                    if title in budget._fields:
                        if budget._fields[title].type == 'many2one':
                            budget_sheet.write(row, col, budget[title].name)
                        elif budget._fields[title].type not in ('many2many',
                                                                'one2many',):
                            budget_sheet.write(row, col, budget[title])
                        else:
                            # if field is one2many it stores the line number
                            project_detail_row = row
                            line_field = title

            line_row = project_detail_row
            # update the lines
            for line in budget[line_field]:
                fy1_col = 0
                fy5_col = 0
                for line_col in range(template_sheet.ncols):
                    if line_row == project_detail_row:
                        line_title = \
                            template_sheet.cell_value(line_row, line_col)
                        line_title = line_title.split('/')
                        # manage the dictionary for mapping columns and fields
                        # data like {1: 'c_or_n'}
                        if len(line_title) > 1:
                            if line_col not in project_detail_title.keys():
                                project_detail_title[line_col] = line_title[1]
                        else:
                            if line_col not in project_detail_title.keys():
                                project_detail_title[line_col] = line_title[0]
                    prepare_title = project_detail_title[line_col]
                    # now update the line cells with related fields value
                    if prepare_title in line._fields.keys():
                        if line._fields[prepare_title].type == 'many2one':
                            budget_sheet.write(line_row, line_col,
                                               line[prepare_title].name)
                        elif line._fields[prepare_title].type not in\
                                ('many2many', 'one2many', ):
                            if prepare_title == 'fy1':
                                fy1_col = line_col
                            if prepare_title == 'fy5':
                                fy5_col = line_col
                            # auto-sum formula to total cell
                            if prepare_title == 'total':
                                cell_range =\
                                    rowcol_pair_to_cellrange(
                                        line_row,
                                        fy1_col, line_row, fy5_col,
                                        row1_abs=False, col1_abs=False,
                                        row2_abs=False, col2_abs=False)
                                total_formula = "SUM(%s)" % (cell_range)
                                budget_sheet.write(
                                    line_row, line_col,
                                    xlwt.Formula(total_formula), num_style)
                            else:
                                # apply numeric format to float type cells
                                if line._fields[prepare_title].type == 'float':
                                    budget_sheet.write(line_row, line_col,
                                                       line[prepare_title],
                                                       num_style)
                                else:
                                    budget_sheet.write(line_row, line_col,
                                                       line[prepare_title])
                    else:
                        budget_sheet.write(line_row, line_col, '')
                line_row += 1
            # make 500 rows editable after lines
            editable_row = 500
            for row_no in range(line_row, editable_row):
                budget_sheet.row(row_no).set_style(editable)

            stream = cStringIO.StringIO()
            workbook.save(stream)
            filename = '%s.xls' % (template_file.name)
            self.env.cr.execute(""" DELETE FROM budget_xls_output """)
            attach_id = self.env['budget.xls.output'].create(
                {'name': filename,
                 'xls_output': base64.encodestring(stream.getvalue()),
                 }
            )
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
