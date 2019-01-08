from openerp import models, fields, api


class XLSXAccountAnalyticLineview(models.TransientModel):
    _name = 'xlsx.account.analytic.line.view'
    _inherit = 'xlsx.report'

    # Search Criteria

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
        domain = []
        self.results = self.env['account.analytic.line.view'].\
            search(domain, limit=100)
