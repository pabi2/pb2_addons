# -*- coding: utf-8 -*-
from openerp import models, api
from .budget_common_report_wizard \
    import BudgetPlanCommonAnalysisReportWizard as BPCWizard


class BudgetPlanUnitAnalysisReportWizard(models.Model, BPCWizard):

    _name = 'budget.plan.unit.analysis.report.wizard'

    @api.multi
    def xls_export(self):
        fields = self._get_fields()
        report_name = 'budget_plan_unit_analysis_report_xls'
        return self._get_report(fields, report_name)
