# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import xlrd
import sys
from openerp import tools
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class BudgetImportWizard(models.Model):
    _name = 'budget.import.wizard'

    input_file = fields.Binary('Template')

    @api.multi
    def update_budget_prepare(self, budget_ids, template=None):
        if not template:
            raise Warning(_('Please add .xlsx template.'))
        if not budget_ids:
            raise Warning(_('No budget to import.'))

        try:
            workbook = xlrd.open_workbook(
                file_contents=base64.decodestring(template),
                formatting_info=True,
            )
        except IOError as e:
            raise Warning(_('Import Error!'), _(e.strerror))
        except ValueError as e:
            raise Warning(_('Import Error!'), _(e.strerror))
        except:
            e = sys.exc_info()[0]
            raise Warning(_('Import Error!'),
                          _('Wrong file format. Please enter .xlsx file.'))
        budgets = self.env['account.budget.prepare'].browse(budget_ids)

        for budget in budgets:
            budget_sheet = workbook.sheet_by_index(0)
            template_sheet = workbook.sheet_by_index(1)
            budget_line_col = {}

            new_data_row = 0
            # find starting line for update budget line from data sheet
            for row in range(budget_sheet.nrows):
                xfx = budget_sheet.cell_xf_index(row, 1)
                xf = workbook.xf_list[xfx]
                cell_lock = xf.protection.cell_locked
                if not cell_lock:
                    new_data_row = row
                    break
            line_row = 0
            line_field = False
            # find budget lines row with field names from template sheet
            for row in range(template_sheet.nrows):
                for col in range(template_sheet.ncols):
                    title = \
                        template_sheet.cell_value(row, col)
                    title = title.split('/')
                    if title and title[0]:
                        if title[0] in budget._fields.keys():
                            if budget._fields[title[0]].type == 'one2many':
                                line_row = row
                                line_field = title[0]
                                break
            # make dictionary with field name and column number
            for col in range(template_sheet.ncols):
                line_title = \
                        template_sheet.cell_value(line_row, col)
                line_title = line_title.split('/')
                # manage the dictionary for mapping columns and fields
                # data like {1: 'c_or_n'}
                if len(line_title) > 1:
                    if col not in budget_line_col.keys():
                        budget_line_col[col] = line_title[1]
                else:
                    if col not in budget_line_col.keys():
                        budget_line_col[col] = line_title[0]

            field_list = []
            data_list = []
            # update the budget lines
            field_list.append('prepare_id')
            for row in range(new_data_row, budget_sheet.nrows):
                line_data = []
                line_data.append(tools.ustr(budget.name))
                for col in range(budget_sheet.ncols):
                    cellvalue = budget_sheet.cell_value(row, col)
                    field = budget_line_col[col]
                    if field in budget[line_field]._fields.keys():
                        if field not in field_list:
                            field_list.append(field)
                        line_data.append(tools.ustr(cellvalue))
                data_list.append(line_data)
            result = self.env['account.budget.prepare.line'].\
                load(field_list, data_list)
            return result

    @api.multi
    def import_budget(self):
        budget_ids = self.env.context.get('active_ids')
        self.update_budget_prepare(budget_ids, self.input_file)
