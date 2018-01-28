# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .budget_common_report_wizard import BudgetCommonReportWizard


class BudgetDetailReportWizard(models.Model, BudgetCommonReportWizard):
    _name = 'budget.detail.report.wizard'

    chart_view = fields.Selection(
        [('personnel', 'Personnel'),
         ('invest_asset', 'Investment Asset'),
         ('unit_base', 'Unit Based'),
         ('project_base', 'Project Based'),
         ('invest_construction', 'Investment Construction')],
        string='Budget View',
        required=True,
    )

    @api.multi
    def xls_export(self):
        fields = ['period_id', 'costcenter_id', 'chart_view']
        report_name = 'budget_detail_report_xls'
        return self._get_report(fields, report_name)
