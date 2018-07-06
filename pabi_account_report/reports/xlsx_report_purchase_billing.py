# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools


class PurchaseBillingView(models.Model):
    _name = 'purchase.billing.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        readonly=True,
    )
    billing_id = fields.Many2one(
        'purchase.billing',
        string='Purchase Billing',
        readonly=True,
    )
    billing_name = fields.Char(
        string='Billing Name',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY inv.id, billing.id) AS id,
                   inv.id AS invoice_id, billing.id AS billing_id,
                   billing.name AS billing_name
            FROM account_invoice inv
            LEFT JOIN purchase_billing billing
                ON inv.purchase_billing_id = billing.id
            WHERE inv.type IN ('in_invoice', 'in_refund') AND
                  billing.id IS NOT NULL AND inv.state IN ('draft', 'open')
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportPurchaseBilling(models.TransientModel):
    _name = 'xlsx.report.purchase.billing'
    _inherit = 'report.account.common'

    filter = fields.Selection(
        [('filter_no', 'No Filters'),
         ('filter_billing_date', 'Billing Dates'),
         ('filter_billing_due_date', 'Billing Due Dates')],
        required=True,
        default='filter_no',
    )
    date_billing_start = fields.Date(
        string='Start Billing Date',
    )
    date_billing_end = fields.Date(
        string='End Billing Date',
    )
    date_due_billing_start = fields.Date(
        string='Start Billing Due Date',
    )
    date_due_billing_end = fields.Date(
        string='End Billing Due Date',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partner',
    )
    billing_ids = fields.Many2many(
        'purchase.billing',
        string='Billing',
        domain=[('state', '=', 'billed')],
    )
    results = fields.Many2many(
        'purchase.billing.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.onchange('filter')
    def _onchange_filter(self):
        super(XLSXReportPurchaseBilling, self)._onchange_filter()
        self.date_billing_start = False
        self.date_billing_end = False
        self.date_due_billing_start = False
        self.date_due_billing_end = False

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['purchase.billing.view']
        dom = []
        if self.date_billing_start:
            dom += [('billing_id.date', '>=', self.date_billing_start)]
        if self.date_billing_end:
            dom += [('billing_id.date', '<=', self.date_billing_end)]
        if self.date_due_billing_start:
            dom += [('billing_id.date_due', '>=', self.date_due_billing_start)]
        if self.date_due_billing_end:
            dom += [('billing_id.date_due', '<=', self.date_due_billing_end)]
        if self.partner_ids:
            dom += [('billing_id.partner_id', 'in', self.partner_ids.ids)]
        if self.billing_ids:
            dom += [('billing_id.id', 'in', self.billing_ids.ids)]
        self.results = Result.search(dom, order="billing_name")
