# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .budget_common_report_wizard import Common


class BudgetPlanUnitAnalysisReportWizard(models.TransientModel, Common):

    _name = 'budget.plan.unit.analysis.report.wizard'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Financial Year',
        required=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    sector_id = fields.Many2one(
        'res.sector',
        string='Sector',
    )
    subsector_id = fields.Many2one(
        'res.subsector',
        string='Subsector',
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
        default='expense',
    )

    @api.multi
    def xls_export(self):
        fields = ['fiscalyear_id', 'org_id', 'sector_id', 'subsector_id',
                  'division_id', 'section_id', 'budget_method']
        report_name = 'budget_plan_unit_analysis_report_xls'
        return self._get_report(fields, report_name)
