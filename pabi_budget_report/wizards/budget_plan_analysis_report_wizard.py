# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class BudgetPlanAnalysisReportWizard(models.Model):
    _name = 'budget.plan.analysis.report.wizard'

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
        data = {}
        fields = ['fiscalyear_id', 'org_id', 'sector_id', 'subsector_id',
                  'division_id', 'section_id', 'budget_method']
        data['form'] = self.read(fields)[0]
        for field in fields:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        if self._context.copy().get('xls_export', False):
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'budget_plan_analysis_report_xls',
                'datas': data,
            }
        raise except_orm(_('Error !'), ('The report has not yet.'))
