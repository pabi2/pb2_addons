# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportBudgetPlanConstructionAnalysis(models.TransientModel):
    _name = 'xlsx.report.budget.plan.construction.analysis'
    _inherit = 'xlsx.report'

    # Search Criteria
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    invest_construction_id = fields.Many2one(
        'res.invest.construction',
        string='Project (C)',
    )
    # Report Result
    results = fields.Many2many(
        'budget.plan.invest.construction.line',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['budget.plan.invest.construction.line']
        dom = [('fiscalyear_id', '=', self.fiscalyear_id.id)]
        if self.org_id:
            dom += [('org_id', '=', self.org_id.id)]
        if self.invest_construction_id:
            dom += [('invest_construction_id', '=',
                     self.invest_construction_id.id)]
        self.results = Result.search(dom)
