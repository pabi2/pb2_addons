from openerp import models, fields, api


class XLSXReportBudgetPlanPersonnelAnalysis(models.TransientModel):
    _name = 'xlsx.report.budget.plan.personnel.analysis'
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
        'budget.plan.personnel.line',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['budget.plan.personnel.line']
        dom = [('fiscalyear_id', '=', self.fiscalyear_id.id)]
        if self.org_id:
            dom += [('org_id', '=', self.org_id.id)]
        if self.sector_id:
            dom += [('sector_id', '=', self.sector_id.id)]
        if self.subsector_id:
            dom += [('subsector_id', '=', self.subsector_id.id)]
        if self.division_id:
            dom += [('division_id', '=', self.division_id.id)]
        if self.section_id:
            dom += [('section_id', '=', self.section_id.id)]
        if self.budget_method:
            dom += [('budget_method', '=', self.budget_method)]
        if self.status:
            dom += [('state', '=', self.status)]
        self.results = Result.search(dom)
