# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools


class CDReceivablePlanningView(models.Model):
    _name = 'cd.receivable.planning.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    loan_agreement_id = fields.Many2one(
        'loan.customer.agreement',
        string='Loan Agreement',
        reaonly=True,
    )
    invoice_plan_id = fields.Many2one(
        'sale.invoice.plan',
        string='Invoice Plan',
        readonly=True,
    )
    fiscalyear_name = fields.Char(
        string='Fiscalyear',
        readonly=True,
    )
    q1 = fields.Float(
        string='Quater 1',
        readonly=True,
    )
    q2 = fields.Float(
        string='Quater 2',
        readonly=True,
    )
    q3 = fields.Float(
        string='Quater 3',
        readonly=True,
    )
    q4 = fields.Float(
        string='Quater 4',
        readonly=True,
    )
    amount_total = fields.Float(
        string='Total Amount',
        compute='_compute_amount_total',
        readonly=True,
    )

    @api.multi
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = rec.q1 + rec.q2 + rec.q3 + rec.q4

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY lca.id, sip.id,af.name) AS id,
                   lca.id AS loan_agreement_id,
                   sip.id AS invoice_plan_id,
                   af.name AS fiscalyear_name,
                   CASE WHEN sip.date_invoice >= af.date_start AND
                    sip.date_invoice <= DATE_TRUNC('month', af.date_start) +
                    INTERVAL '3 month' - INTERVAL '1 day'
                    THEN sip.subtotal ELSE 0 END AS q1,
                   CASE WHEN sip.date_invoice >=
                    af.date_start + INTERVAL '3 month' AND
                    sip.date_invoice <= DATE_TRUNC('month', af.date_start) +
                    INTERVAL '6 month' - INTERVAL '1 day'
                    THEN sip.subtotal ELSE 0 END AS q2,
                   CASE WHEN sip.date_invoice >=
                    af.date_start + INTERVAL '6 month' AND
                    sip.date_invoice <= DATE_TRUNC('month', af.date_start) +
                    INTERVAL '9 month' - INTERVAL '1 day'
                    THEN sip.subtotal ELSE 0 END AS q3,
                   CASE WHEN sip.date_invoice >=
                    af.date_start + INTERVAL '9 month' AND
                    sip.date_invoice <= DATE_TRUNC('month', af.date_start) +
                    INTERVAL '12 month' - INTERVAL '1 day'
                    THEN sip.subtotal ELSE 0 END AS q4
            FROM loan_customer_agreement lca
            LEFT JOIN sale_order so ON lca.sale_id = so.id
            LEFT JOIN sale_invoice_plan sip ON so.id = sip.order_id
            LEFT JOIN account_fiscalyear af ON
                sip.date_invoice >= af.date_start AND
                sip.date_invoice <= af.date_stop
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportCDReceivablePlanning(models.TransientModel):
    _name = 'xlsx.report.cd.receivable.planning'
    _inherit = 'report.account.common'

    partner_ids = fields.Many2many(
        'res.partner',
        string='Customers',
    )
    bank_ids = fields.Many2many(
        'res.bank',
        string='Banks',
    )
    results = fields.Many2many(
        'cd.receivable.planning.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        """
        Solution
        1. State supplier invoice to paid
        2. State sale order not in ('draft', 'cancel')
        """
        self.ensure_one()
        Result = self.env['cd.receivable.planning.view']
        dom = \
            [('loan_agreement_id.supplier_invoice_id.state', '=', 'paid'),
             ('invoice_plan_id.order_id.state', 'not in', ('draft', 'cancel'))]
        if self.fiscalyear_start_id:
            dom += [('invoice_plan_id.date_invoice', '>=',
                     self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('invoice_plan_id.date_invoice', '<=',
                     self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('invoice_plan_id.date_invoice', '>=',
                     self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('invoice_plan_id.date_invoice', '<=',
                     self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('invoice_plan_id.date_invoice', '>=', self.date_start)]
        if self.date_end:
            dom += [('invoice_plan_id.date_invoice', '<=', self.date_end)]
        if self.partner_ids:
            dom += [('loan_agreement_id.borrower_partner_id', 'in',
                     self.partner_ids.ids)]
        if self.bank_ids:
            dom += [('loan_agreement_id.bank_id.bank', 'in',
                     self.bank_ids.ids)]
        self.results = Result.search(dom, order="fiscalyear_name")
