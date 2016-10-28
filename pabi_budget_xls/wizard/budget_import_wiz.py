# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import sys
import cStringIO

import openpyxl

from openerp import tools
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class BudgetImportWizard(models.Model):
    _name = 'budget.import.wizard'

    input_file = fields.Binary('Template')
    datas_fname = fields.Char('File Path')

    @api.multi
    def update_budget_prepare(self, budget_ids, template=None):
        if not template:
            raise UserError(_('Please add .xlsx template.'))
        if not budget_ids:
            raise UserError(_('No budget to import.'))

        imp_file = template.decode('base64')
        stream = cStringIO.StringIO(imp_file)

        try:
            workbook = openpyxl.load_workbook(stream)
        except IOError as e:
            raise UserError(_(e.strerror))
        except ValueError as e:
            raise UserError(_(e.strerror))
        except:
            e = sys.exc_info()[0]
            raise UserError(_('Wrong file format. Please enter .xlsx file.'))
        budgets = self.env['budget.plan.unit'].browse(budget_ids)
        for budget in budgets:
            if budget.state != 'draft':
                raise UserError(
                    _('You can update budget plan only in draft state!'))

            NonCostCtrl_Sheet = workbook.get_sheet_by_name('Non_CostControl')
            max_row = NonCostCtrl_Sheet.max_row
            vals = {}

            bg_id = NonCostCtrl_Sheet.cell(row=1, column=5).value
            if budget.id != bg_id:
                raise UserError(
                    _('Validation Error\n Please enter plan related file!')
                )

            fiscal_year = NonCostCtrl_Sheet.cell(row=1, column=2).value
            fiscal_year_id = self.env['account.fiscalyear'].search(
                [('name', '=', tools.ustr(fiscal_year))])
            if fiscal_year_id:
                vals.update({'fiscalyear_id': fiscal_year_id.id})

            org = NonCostCtrl_Sheet.cell(row=2, column=2).value
            org_id =\
                self.env['res.org'].search(['|',
                                            ('code', '=', tools.ustr(org)),
                                            ('name_short', '=', tools.ustr(org))])
            if org_id:
                vals.update({'org_id': org_id.id})

            section = NonCostCtrl_Sheet.cell(row=3, column=2).value
            section_id = self.env['res.section'].search(
                [('code', '=', tools.ustr(section))])
            if section_id:
                vals.update({'section_id': section_id.id})

            export_date = NonCostCtrl_Sheet.cell(row=4, column=2).value
            if export_date:
                vals.update({'date': export_date})

            responsible_by = NonCostCtrl_Sheet.cell(row=5, column=2).value
            responsible_by_id = self.env['res.users'].search(
                [('name', '=', tools.ustr(responsible_by))])
            if section_id:
                vals.update({'creating_user_id': responsible_by_id.id})

            line_row = 11
            lines = {}
            lines_to_create = []
            for row in range(line_row, max_row):
                line_vals = {}
                line_vals.update({'section_id': section_id.id,
                                  'plan_id': budget.id})
                ag_group = NonCostCtrl_Sheet.cell(row=row, column=4).value
                if not ag_group:
                    break
                ag_group_id = self.env['account.activity.group'].search(
                    [('name', '=', tools.ustr(ag_group))])
                if ag_group_id:
                    line_vals.update({'activity_group_id': ag_group_id.id})

                unit = NonCostCtrl_Sheet.cell(row=row, column=7).value
                act_unitprice = NonCostCtrl_Sheet.cell(row=row, column=8).value
                activity_unit = NonCostCtrl_Sheet.cell(row=row, column=9).value
                line_vals.update({
                    'unit': unit,
                    'activity_unit_price': act_unitprice,
                    'activity_unit': activity_unit,
                })
                line_id = NonCostCtrl_Sheet.cell(row=row, column=26).value
                p = 0
                col = 11
                while p != 13:
                    val = NonCostCtrl_Sheet.cell(row=row, column=col).value
                    line_vals.update({'m' + str(p): val})
                    if col == 23:
                        break
                    col += 1
                    p += 1
                if line_id:
                    lines.update({int(line_id): line_vals})
                else:
                    lines_to_create.append(line_vals)
            for line in budget.plan_line_ids:
                if lines.get(line.id, False):
                    line.write(lines[line.id])
            for line in lines_to_create:
                self.env['budget.plan.unit.line'].create(line)
            budget.write(vals)
            attachement_id = self.env['ir.attachment'].create({
                'name': self.datas_fname,
                'datas': stream.getvalue().encode('base64'),
                'datas_fname': self.datas_fname,
                'res_model': 'budget.plan.unit',
                'res_id': budget.id,
            })
            self.env['budget.plan.history'].create({
                'user_id': self.env.user.id,
                'operation_date': fields.Datetime.now(),
                'operation_type': 'import',
                'plan_id': budget.id,
                'attachement_id': attachement_id.id
            })
            return {}

    @api.multi
    def import_budget(self):
        budget_ids = self.env.context.get('active_ids')
        result = self.update_budget_prepare(budget_ids, self.input_file)
        if result.get('messages'):
            msg = False
            for line in result['messages']:
                if not msg:
                    msg = line['message']
                else:
                    msg = msg + '\n' + line['message']
            if msg:
                raise UserError(_('%s') % (msg,))
