# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class BudgetDetailReportWizard(models.Model):
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
        data = {}
        data['form'] = self.read(
            ['period_id', 'costcenter_id', 'chart_view'])[0]
        for field in ['period_id', 'costcenter_id', 'chart_view']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        if self._context.copy().get('xls_export', False):
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'budget_detail_report_xls',
                'datas': data,
            }
        raise except_orm(_('Error !'), ('The report has not yet.'))
