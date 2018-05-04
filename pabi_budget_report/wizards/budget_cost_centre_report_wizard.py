# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .budget_common_report_wizard import Common


class BudgetCostCentreReportWizard(models.TransientModel, Common):
    _name = 'budget.cost.centre.report.wizard'

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

    @api.multi
    def xls_export(self):
        fields = ['period_id', 'costcenter_id']
        report_name = 'budget_cost_centre_report_xls'
        return self._get_report(fields, report_name)
