from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class XLSXReporAdvanceStatus(models.TransientModel):
    _name = 'xlsx.report.advance.status'
    _inherit = 'xlsx.report'

    # Search Criteria
    run_date = fields.Date(
        string='Run Date',
        default=lambda self: fields.Date.context_today(self),
    )
    # Report Result
    results = fields.Many2many(
        'hr.expense.expense',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['hr.expense.expense']
        dom = [('state', '=', 'paid'), ('amount_to_clearing', '>', 0.0)]
        self.results = Result.search(
            dom, order='operating_unit_id, employee_id, invoice_id')
