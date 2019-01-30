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
    line_filter = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    action_type = fields.Selection(
        default=lambda self: self._context.get('action_type', False),
    )

    @api.onchange('line_filter')
    def _onchange_line_filter(self):
        self.chartfield_ids = []
        Chartfield = self.env['chartfield.view']
        dom = []
        if self.line_filter:
            codes = self.line_filter.split('\n')
            codes = [x.strip() for x in codes]
            codes = ','.join(codes)
            dom.append(('code', 'ilike', codes))
            self.chartfield_ids = Chartfield.search(dom, order='id')

    # Following onchange is required
    @api.onchange('charge_type', 'group_by_charge_type',
                  'activity_id', 'group_by_activity_id',
                  'activity_group_id', 'group_by_activity_group_id',
                  'section_id', 'group_by_section_id',
                  'org_id', 'group_by_org_id',
                  'project_id', 'group_by_project_id',
                  'invest_asset_id', 'group_by_invest_asset_id',
                  'invest_construction_id', 'group_by_invest_construction_id',
                  'group_by_invest_construction_phase_id', 'chartfield_id',
                  'group_by_chartfield_id', 'section_ids', 'project_ids')
    def _onchange_helper(self):
        """ Ensure sure that, if some field is selected, so do some groupby """
        # For budget overview report
        if self.charge_type:
            self.group_by_charge_type = True
        if self.activity_id:
            self.group_by_activity_id = True
        if self.activity_group_id:
            self.group_by_activity_group_id = True
        # --
        if self.section_id:
            self.group_by_section_id = True
        if self.org_id:
            self.group_by_org_id = True
        if self.project_id:
            self.group_by_project_id = True
        if self.invest_asset_id:
            self.group_by_invest_asset_id = True
        if self.invest_construction_id:
            self.group_by_invest_construction_id = True
        if self.chartfield_id:
            self.group_by_chartfield_id = True
        # For my budget report
        if self.section_ids:
            self.group_by_section_id = True
        if self.project_ids:
            self.group_by_project_id = True

    @api.onchange('report_type')
    def _onchange_report_type(self):
        super(BudgetDrilldownReportWizard, self)._onchange_report_type()
        # Clear Data
        for field in ['org_id', 'section_id', 'project_id', 'invest_asset_id',
                      'invest_construction_id', 'personnel_costcenter_id',
                      'activity_group_id', 'charge_type', 'activity_id',
                      'chartfield_id']:
            self['group_by_%s' % field] = False

        """ Default Group By to True - by Report Type """
        groupby_chartfield = []
        if self.report_type == 'all':
            groupby_chartfield.append('chartfield_id')
        if self.report_type in REPORT_GROUPBY.keys():
            for field in REPORT_GROUPBY[self.report_type] + groupby_chartfield:
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
