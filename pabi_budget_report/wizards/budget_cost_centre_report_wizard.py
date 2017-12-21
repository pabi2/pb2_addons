# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class BudgetCostCentreReportWizard(models.Model):
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
        data = {}
        data['form'] = self.read(['period_id', 'costcenter_id'])[0]
        for field in ['period_id', 'costcenter_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        if self._context.copy().get('xls_export', False):
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'budget_cost_centre_report_xls',
                'datas': data,
            }
        raise except_orm(_('Error !'), ('The report has not yet.'))
