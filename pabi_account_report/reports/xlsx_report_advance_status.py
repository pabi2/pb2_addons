from datetime import datetime
from dateutil.relativedelta import relativedelta
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


class HRExpenseExpense(models.Model):
    """ Add compute field for reporting purposes """
    _inherit = 'hr.expense.expense'

    amount_clearing_0 = fields.Float(
        string='Not Overdue',
        compute='_compute_clearing_amount',
    )
    amount_clearing_1 = fields.Float(
        string='Overdue 1-15 Days',
        compute='_compute_clearing_amount',
    )
    amount_clearing_2 = fields.Float(
        string='Overdue 16-30 Days',
        compute='_compute_clearing_amount',
    )
    amount_clearing_3 = fields.Float(
        string='Overdue >30 Days',
        compute='_compute_clearing_amount',
    )

    @api.multi
    def _compute_clearing_amount(self):
        today = datetime.strptime(fields.Date.context_today(self), '%Y-%m-%d')
        for rec in self:
            if not rec.date_due:
                continue
            date_due = datetime.strptime(rec.date_due, '%Y-%m-%d')
            days_diff = (today - date_due).days
            if days_diff < 1:
                rec.amount_clearing_0 = rec.amount_to_clearing
            elif days_diff >= 1 and days_diff <= 15:
                rec.amount_clearing_1 = rec.amount_to_clearing
            elif days_diff >= 16 and days_diff <= 30:
                rec.amount_clearing_2 = rec.amount_to_clearing
            elif days_diff >= 1 and days_diff > 30:
                rec.amount_clearing_3 = rec.amount_to_clearing
