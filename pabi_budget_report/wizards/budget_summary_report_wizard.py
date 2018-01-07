# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class BudgetSummaryReportWizard(models.Model):
    _name = 'budget.summary.report.wizard'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
    )

    @api.multi
    def xls_export(self):
        data = {}
        data['form'] = self.read(['fiscalyear_id'])[0]
        for field in ['fiscalyear_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        if self._context.copy().get('xls_export', False):
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'budget_summary_report_xls',
                'datas': data,
            }
        raise except_orm(_('Error !'), ('The report has not yet.'))
