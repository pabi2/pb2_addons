# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .budget_common_report_wizard import Common


class BudgetDetailReportWizard(models.TransientModel, Common):
    _name = 'budget.detail.report.wizard'

    period_id = fields.Many2one(
        'account.period',
        string='Period End',
        required=True,
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Cost Center',
        required=True,
    )
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
