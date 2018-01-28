# -*- coding: utf-8 -*-
from openerp import models, api
from .budget_common_report_wizard import BudgetCommonReportWizard


class BudgetCostCentreReportWizard(models.Model, BudgetCommonReportWizard):
    _name = 'budget.cost.centre.report.wizard'

    @api.multi
    def xls_export(self):
        fields = ['period_id', 'costcenter_id']
        report_name = 'budget_cost_centre_report_xls'
        return self._get_report(fields, report_name)
