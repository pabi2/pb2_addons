# -*- coding: utf-8 -*-
from openerp import fields, api, _
from openerp.exceptions import except_orm


class Common(object):

    @api.multi
    def _get_report(self, fields, report_name=False):
        data = {}
        data['form'] = self.read(fields)[0]
        for field in fields:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        if self._context.copy().get('xls_export', False) and report_name:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': report_name,
                'datas': data,
            }
        raise except_orm(_('Error !'), ('No report.'))


class BudgetCommonReportWizard(Common):

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


class BudgetPlanCommonAnalysisReportWizard(Common):

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

    @api.model
    def _get_fields(self):
        fields = ['fiscalyear_id', 'org_id', 'sector_id', 'subsector_id',
                  'division_id', 'section_id', 'budget_method']
        return fields
