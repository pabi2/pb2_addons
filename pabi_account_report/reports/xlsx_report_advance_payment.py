# -*- coding: utf-8 -*
from openerp import models, fields, api, tools


class XLSXReportAdvancePayment(models.TransientModel):
    _name = 'xlsx.report.advance.payment'
    _inherit = 'report.account.common'

    fiscalyear_start_id = fields.Many2one(
        default=False,
    )
    fiscalyear_end_id = fields.Many2one(
        default=False,
    )
    filter = fields.Selection(
        readonly=True,
        default='filter_date',
    )
    date_report = fields.Date(
        string='Report Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    account_ids = fields.Many2many(
        'account.account',
        string='Account',
        help='''Only selected accounts will be printed.
                Leave empty to print all accounts.''',
        readonly="1",
        default=lambda self: self.env.user.company_id.account_deposit_supplier,
    )
    results = fields.Many2many(
        'advance.payment.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        # Execute view
        Result = self.env['advance.payment.view']
        Result._execute_view(self.account_ids[0].id, self.date_report)
        # Get View
        self.results = Result.search([])


class AdvancePaymentView(models.Model):
    _name = 'advance.payment.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    auto_reconcile_id = fields.Many2one(
        'account.auto.reconcile',
        string='Auto Reconciled',
        readonly=True
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        readonly=True,
    )
    balance = fields.Float(
        string='Balance',
        readonly=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        readonly=True,
    )

    def _get_sql_view(self, account_id, date_report):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY m.auto_reconcile_id, l.org_id)
                    AS id, l.org_id,
                   m.auto_reconcile_id, SUM(l.debit - l.credit) AS balance,
                   MIN(inv.id) AS invoice_id
            FROM account_move_line l
            LEFT JOIN account_move m ON l.move_id = m.id
            LEFT JOIN account_invoice inv ON m.id = inv.move_id
            WHERE l.account_id = %s AND
                (l.date_reconciled IS NULL OR l.date_reconciled > '%s') AND
                l.date_created <= '%s'
            GROUP BY m.auto_reconcile_id, l.org_id
            ORDER BY l.org_id
                """ % (account_id, date_report, date_report)
        return sql_view

    def _execute_view(self, cr, uid, account_id, date_report):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view(
                    account_id, date_report)))
