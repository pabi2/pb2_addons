# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .budget_common_report_wizard import Common


class BudgetSummaryReportWizard(models.TransientModel, Common):
    _name = 'budget.summary.report.wizard'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
    )

    @api.multi
    def xls_export(self):
        fields = ['fiscalyear_id']
        report_name = 'budget_summary_report_xls'
        return self._get_report(fields, report_name)
