from openerp import models, fields, api


class XLSXAccountAnalyticLineview(models.TransientModel):
    _name = 'xlsx.account.analytic.line.view'
    _inherit = 'xlsx.report'

    # Search Criteria
    type_commit = fields.Selection(
        [('so_commit', 'SO Commitment'),
         ('pr_commit', 'PR Commitment'),
         ('po_commit', 'PO Commitment'),
         ('exp_commit', 'Expense Commitment'),
         ('total_commit', 'Total Commitment'),
         ('actual', 'Actual'),
         ],
        default=lambda self: self._context.get('type_commit', False),
        string='Type',
        readonly=True,
    )

    # Report Result
    results = fields.Many2many(
        'account.analytic.line.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        analytic_line_ids = self._context.get('analytic_line_ids', False)
        if analytic_line_ids:
            domain = [('id', 'in', analytic_line_ids)]
            self.results = self.env['account.analytic.line.view'].\
                search(domain)
