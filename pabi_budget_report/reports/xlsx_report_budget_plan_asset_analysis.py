from openerp import models, fields, api


class XLSXReportBudgetPlanAssetAnalysis(models.TransientModel):
    _name = 'xlsx.report.budget.plan.asset.analysis'
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
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
    )
    status = fields.Selection(
        [('1_draft', 'Draft'),
         ('4_cancel', 'Cancelled'),
         ('7_accept', 'Accepted'),
         ('8_done', 'Done'), ],
        string='State',
    )
    # Report Result
    results = fields.Many2many(
        'budget.plan.invest.asset.line',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['budget.plan.invest.asset.line']
        dom = [('fiscalyear_id', '=', self.fiscalyear_id.id)]
        if self.org_id:
            dom += [('org_id', '=', self.org_id.id)]
        if self.activity_group_id:
            dom += [('activity_group_id', '=', self.activity_group_id.id)]
        if self.activity_id:
            dom += [('activity_id', '=', self.activity_id.id)]
        if self.budget_method:
            dom += [('budget_method', '=', self.budget_method)]
        if self.status:
            dom += [('state', '=', self.status)]
        self.results = Result.search(dom)
