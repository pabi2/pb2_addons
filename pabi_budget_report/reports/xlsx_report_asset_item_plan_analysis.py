# -*- coding: utf-8 -*-
from openerp import models, fields, api


class XLSXReportAssetItemPlanAnalysis(models.TransientModel):
    _name = 'xlsx.report.asset.item.plan.analysis'
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
    owner_section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    # Report Result
    results = fields.Many2many(
        'invest.asset.plan.item',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['invest.asset.plan.item']
        dom = [('fiscalyear_id', '=', self.fiscalyear_id.id)]
        if self.org_id:
            dom += [('org_id', '=', self.org_id.id)]
        if self.owner_section_id:
            dom += [('owner_section_id', '=', self.owner_section_id.id)]
        self.results = Result.search(dom)
