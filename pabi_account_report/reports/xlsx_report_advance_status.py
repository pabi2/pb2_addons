# -*- coding: utf-8 -*-
from openerp import models, fields, api


class XLSXReportAdvanceStatus(models.TransientModel):
    _name = 'xlsx.report.advance.status'
    _inherit = 'report.account.common'

    filter = fields.Selection(
        default='filter_date',
        readonly=True,
    )
    date_report = fields.Date(
        string='Report Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Employee',
    )
    status = fields.Many2many(
        'xlsx.report.status',
        string='Stauts',
        domain=[('location', '=', 'hr.expense.expense')],
    )
    results = fields.Many2many(
        'hr.expense.expense',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
  

    @api.model
    def _get_expense_id(self, date_report):
        self._cr.execute("""
            SELECT expense.id
            FROM hr_expense_expense expense
            LEFT JOIN hr_expense_clearing clearing
                ON expense.id = clearing.advance_expense_id
            WHERE expense.is_employee_advance = TRUE AND
                expense.amount_advanced IS NOT NULL
            GROUP BY expense.id
            HAVING expense.amount_advanced >
                SUM(CASE WHEN clearing.id IS NULL THEN 0
                         WHEN clearing.date <= '%s' THEN (CASE WHEN clearing.clearing_amount IS NULL THEN 0 ELSE clearing.clearing_amount END)
                         ELSE 0 END)
        """ % (date_report, ))
        return map(lambda l: l[0], self._cr.fetchall())

    @api.multi
    def _compute_results(self):
        """
        Snap Short
        Filter domain
        1. Check for employee advance (is_employee_advance = True)
        2. Check paid date of employee advance
           2.1 Must be only paid (date_paid != False)
           2.2 Must paid already at report date (date_paid <= date_report)
        3. Not clear advance at report date (Check from _get_expense_id)
        """
        self.ensure_one()
        date_report = self.date_report
        Result = self.env['hr.expense.expense']
        dom = [('is_employee_advance', '=', True),
               #('state', '!=', 'cancelled'),
               #('invoice_id.date_paid', '!=', False),
               #('invoice_id.date_paid', '<=', date_report),
               ('id', 'in', self._get_expense_id(date_report))]
        if not self.status:
            dom += [('state', 'in', ['draft', 'confirm', 'accepted', 'done', 'invoice_except', 'paid'])]
        elif self.status:
            res = []
            for st in self.status:
                res += [self.env['xlsx.report.status'].browse(st.id).status]
            dom += [('state', 'in', res)]
        if self.employee_ids:
            dom += [('employee_id', 'in', self.employee_ids.ids)]
        self.results = Result.search(
            dom, order="operating_unit_id,employee_id,invoice_id")







