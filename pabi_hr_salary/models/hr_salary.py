# -*- coding: utf-8 -*-
import re
import time
import base64
import openerp
from openerp import models, api
from openerp.exceptions import ValidationError


class HRSalaryExpense(models.Model):
    _inherit = 'hr.salary.expense'

    @api.multi
    def action_submit(self):
        self.ensure_one()
        res = super(HRSalaryExpense, self).action_submit()
        salary_doc = self.print_hr_salary_expense_form()
        # '1' = Submit, '2' = Resubmit, '3' = Cancel
        # Note: I think resubmitted may not be used
        self.send_signal_to_pabiweb('1', salary_doc=salary_doc)
        return res

    @api.multi
    def print_hr_salary_expense_form(self):
        self.ensure_one()
        Attachment = self.env['ir.attachment']
        Report = self.env['ir.actions.report.xml']
        matching_reports = Report.search([
            ('model', '=', self._name),
            ('report_type', '=', 'pdf'),
            ('report_name', '=', 'hr_salary_approval_form_th')])
        if matching_reports:
            report = matching_reports[0]
            result, _ = openerp.report.render_report(self._cr, self._uid,
                                                     [self.id],
                                                     report.report_name,
                                                     {'model': self._name})
            result = base64.b64encode(result)
            file_name = self.name_get()[0][1]
            file_name = re.sub(r'[^a-zA-Z0-9_-]', '_', file_name)
            file_name += ".pdf"
            salary_form = Attachment.create({
                'name': file_name,
                'datas': result,
                'datas_fname': file_name,
                'res_model': self._name,
                'res_id': self.id,
                'type': 'binary'
            })
            return salary_form
        else:
            raise ValidationError(_('Print report action not found!'))
