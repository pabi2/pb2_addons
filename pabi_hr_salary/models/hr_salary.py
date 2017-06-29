# -*- coding: utf-8 -*-
import re
import time
import base64
import openerp
from openerp import models, api


class HRSalaryExpense(models.Model):
    _inherit = 'hr.salary.expense'

    @api.multi
    def action_submit(self):
        self.print_hr_salary_expense_form()
        return super(HRSalaryExpense, self).action_submit()

    @api.multi
    def print_hr_salary_expense_form(self):
        Attachment = self.env['ir.attachment']
        Report = self.env['ir.actions.report.xml']
        for record in self:
            matching_reports = Report.search([
                ('model', '=', self._name),
                ('report_type', '=', 'pdf'),
                ('report_name', '=', 'hr_salary_approval_form_th')])
            if matching_reports:
                report = matching_reports[0]
                result, _ = openerp.report.render_report(self._cr, self._uid,
                                                         [record.id],
                                                         report.report_name,
                                                         {'model': self._name})
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment,
                                                     eval_context):
                    # exist_pd_file = Attachment.search([
                    #     ('res_id', '=', self.id),
                    #     ('res_model', '=', 'purchase.requisition'),
                    #     ('name', 'ilike', '_main_form.pdf'),
                    # ])
                    # if len(exist_pd_file) > 0:
                    #     exist_pd_file.unlink()
                    result = base64.b64encode(result)
                    file_name = self.name_get()[0][1]
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', '_', file_name)
                    file_name += ".pdf"
                    Attachment.create({
                        'name': file_name,
                        'datas': result,
                        'datas_fname': file_name,
                        'res_model': self._name,
                        'res_id': record.id,
                        'type': 'binary'
                    })
