# -*- coding: utf-8 -*
from openerp import models, fields, api, tools


class XLSXReportPurchaseBilling(models.TransientModel):
    _name = 'xlsx.report.purchase.billing'
    _inherit = 'report.account.common'

    fiscalyear_start_id = fields.Many2one(
        default=False,
    )
    fiscalyear_end_id = fields.Many2one(
        default=False,
    )
    filter = fields.Selection(
        [('filter_no', 'No Filters'),
         ('filter_billing_date', 'Billing Dates'),
         ('filter_billing_due_date', 'Billing Due Dates')],
        required=True,
        default='filter_no',
    )
    billing_date_start = fields.Date(
        string='Start Billing Date',
    )
    billing_date_end = fields.Date(
        string='End Billing Date',
    )
    billing_due_date_start = fields.Date(
        string='Start Billing Due Date',
    )
    billing_due_date_end = fields.Date(
        string='End Billing Due Date',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partner',
        domain=[('supplier', '=', True)],
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

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['purchase.billing.view']
        dom = [('invoice_id.purchase_billing_id', '!=', False),
               ('invoice_id.state', 'in', ['draft', 'open'])]
        if self.billing_date_start:
            dom += [('invoice_id.purchase_billing_id.date', '>=',
                     self.billing_date_start)]
        if self.billing_date_end:
            dom += [('invoice_id.purchase_billing_id.date', '<=',
                     self.billing_date_end)]
        if self.billing_due_date_start:
            dom += [('invoice_id.purchase_billing_id.date_due', '>=',
                     self.billing_due_date_start)]
        if self.billing_due_date_end:
            dom += [('invoice_id.purchase_billing_id.date_due', '<=',
                     self.billing_due_date_end)]
        if self.partner_ids:
            dom += [('invoice_id.partner_id', 'in', self.partner_ids.ids)]
        if self.billing_ids:
            dom += [('invoice_id.purchase_billing_id', 'in',
                     self.billing_ids.ids)]
        self.results = Result.search(dom, order="billing_name")


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
    billing_name = fields.Char(
        string='Billing Name',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY inv.id) AS id,
                   inv.id AS invoice_id, billing.name AS billing_name
            FROM account_invoice inv
            LEFT JOIN purchase_billing billing
                ON inv.purchase_billing_id = billing.id
            WHERE inv.type IN ('in_invoice', 'in_refund')
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
