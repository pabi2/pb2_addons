# -*- coding: utf-8 -*-
import re
import base64
import openerp
from openerp import tools
from openerp import models, api, fields
from openerp.exceptions import ValidationError


class HRSalaryExpense(models.Model):
    _inherit = 'hr.salary.expense'

    summary_ids = fields.One2many(
        'hr.salary.summary',
        'salary_id',
        string='Summary',
        readonly=True,
    )
    summary_total = fields.Float(
        string='Summary Total',
        compute='_compute_summary_total',
    )

    @api.multi
    def _compute_summary_total(self):
        for rec in self:
            rec.summary_total = sum(rec.summary_ids.mapped('amount'))

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
            file_name = self.display_name
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


class HRSalaryLine(models.Model):
    _inherit = 'hr.salary.line'
    _order = 'sequence, id'

    sequence = fields.Integer(
        string='Sequence',
        default=1,
        index=True,
        readonly=True,
    )


class HRSalarySummary(models.Model):
    _name = 'hr.salary.summary'
    _auto = False

    salary_id = fields.Many2one(
        'hr.salary.expense',
        string='Salary',
        readonly=True,
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        readonly=True,
    )
    amount = fields.Float(
        string='Amount',
        readonly=True,
    )

    def init(self, cr):
        sql = """
            select min(id) as id, salary_id,
            activity_group_id, sum(amount) as amount
            from hr_salary_line
            where activity_group_id is not null
            group by salary_id, activity_group_id
        """
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, sql))
