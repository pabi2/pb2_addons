# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .budget_common_report_wizard import Common


class BudgetPlanProjectAnaysisReportWizard(models.TransientModel, Common):

    _name = 'budget.plan.project.analysis.report.wizard'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Financial Year',
        required=True,
    )
    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Functional Area',
    )
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group',
    )
    program_id = fields.Many2one(
        'res.program',
        string='Program',
    )
    project_group_id = fields.Many2one(
        'res.project.group',
        string='Project Group',
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
        default='expense',
    )

    @api.multi
    def xls_export(self):
        fields = ['fiscalyear_id', 'functional_area_id', 'program_group_id',
                  'program_id', 'project_group_id', 'project_id',
                  'budget_method']
        report_name = 'budget_plan_project_analysis_report_xls'
        return self._get_report(fields, report_name)
