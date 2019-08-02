from openerp import models, fields, api


class XLSXReportBudgetPlanProjectAnalysis(models.TransientModel):
    _name = 'xlsx.report.budget.plan.project.analysis'
    _inherit = 'xlsx.report'

    # Search Criteria
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Financial Year',
        required=True,
    )
    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Functional Area',
    )
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group',
    )
    program_id = fields.Many2one(
        'res.program',
        string='Program',
    )
    project_group_id = fields.Many2one(
        'res.project.group',
        string='Project Group',
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
    )
    status = fields.Selection(
        [('1_draft', 'Draft'),
         ('4_cancel', 'Cancelled'),
         ('6_verify', 'Verified'),
         ('7_accept', 'Accepted'),
         ('8_done', 'Done'), ],
        string='State',
        default=False,
    )
    # Report Result
    results = fields.Many2many(
        'budget.plan.project.line',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['budget.plan.project.line']
        dom = [('fiscalyear_id', '=', self.fiscalyear_id.id)]
        if self.functional_area_id:
            dom += [('program_id.functional_area_id', '=', self.functional_area_id.id)]
        if self.program_group_id:
            dom += [('program_id.program_group_id', '=', self.program_group_id.id)]
        if self.program_id:
            dom += [('program_id', '=', self.program_id.id)]
        if self.project_group_id:
            dom += [('project_group_id', '=', self.project_group_id.id)]
        if self.project_id:
            dom += [('project_id', '=', self.project_id.id)]
        if self.budget_method:
            dom += [('budget_method', '=', self.budget_method)]
        if self.status:
            dom += [('state', '=', self.status)]
        self.results = Result.search(dom)
