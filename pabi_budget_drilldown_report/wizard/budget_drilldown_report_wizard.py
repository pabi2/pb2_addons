# -*- coding: utf-8 -*-
from openerp import models, fields, api
from ..models.common import SearchCommon


class BudgetDrilldownReportWizard(SearchCommon, models.TransientModel):
    _name = 'budget.drilldown.report.wizard'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        default=lambda self: self.env['account.fiscalyear'].find(),
        required=True,
    )

    @api.multi
    def run_report(self):
        self.ensure_one()
        RPT = self.env['budget.drilldown.report']
        report_id = RPT.generate_report(self)
        action = self.env.ref('pabi_budget_drilldown_report.'
                              'action_budget_drilldown_report')
        result = action.read()[0]
        result.update({'res_id': report_id,
                       'domain': [('id', '=', report_id)]})
        return result
