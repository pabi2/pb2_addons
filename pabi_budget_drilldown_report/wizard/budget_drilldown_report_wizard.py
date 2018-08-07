# -*- coding: utf-8 -*-
from openerp import models, fields, api
from ..models.common import SearchCommon, REPORT_GROUPBY


class BudgetDrilldownReportWizard(SearchCommon, models.TransientModel):
    _name = 'budget.drilldown.report.wizard'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        default=lambda self: self.env['account.fiscalyear'].find(),
        required=True,
    )

    @api.onchange('report_type')
    def _onchange_report_type(self):
        super(BudgetDrilldownReportWizard, self)._onchange_report_type()
        # Clear Data
        for field in ['section_id', 'project_id', 'activity_group_id',
                      'charge_type', 'activity_id']:
            self['group_by_%s' % field] = False

        """ Default Group By to True - by Report Type """
        if self.report_type in REPORT_GROUPBY.keys():
            for field in REPORT_GROUPBY[self.report_type]:
                groupby_field = 'group_by_%s' % field
                self[groupby_field] = True
        return

    @api.multi
    def run_report(self):
        self.ensure_one()
        RPT = self.env['budget.drilldown.report']
        report_id, view_id = RPT.generate_report(self)
        action = self.env.ref('pabi_budget_drilldown_report.'
                              'action_budget_drilldown_report')
        result = action.read()[0]
        result.update({
            'res_id': report_id,
            'domain': [('id', '=', report_id)],
            'views': [(view_id, 'form')],
        })
        return result
