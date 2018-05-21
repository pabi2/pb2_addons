from openerp import models, fields, api


class XLSXReportPurchaseBilling(models.TransientModel):
    _name = 'xlsx.report.purchase.billing'
    _inherit = 'xlsx.report'

    # Search Criteria
    start_billing_date = fields.Date(
        string='Billing Date From',
    )
    end_billing_date = fields.Date(
        string='Billing Date To',
    )
    start_billing_due_date = fields.Date(
        string='Billing Due Date From',
    )
    end_billing_due_date = fields.Date(
        string='Billing Due Date To',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        'xlsx_report_purchase_billing_partner_rel',
        'report_id', 'partner_id',
        string='Supplier(s)',
        domain=[('supplier', '=', True)],
    )
    billing_ids = fields.Many2many(
        'purchase.billing',
        'xlsx_report_purchase_billing_rel',
        'report_id', 'billing_id',
        string='Billing Number(s)',
        domain=[('state', '=', 'billed')],
    )
    # Report Result
    results = fields.Many2many(
        'account.invoice',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['account.invoice']
        dom = [('type', 'in', ['in_invoice', 'in_refund']),
               ('purchase_billing_id', '!=', False),
               ('state', 'in', ['draft', 'open'])]
        if self.start_billing_date:
            dom += [('purchase_billing_id.date', '>=',
                     self.start_billing_date)]
        if self.end_billing_date:
            dom += [('purchase_billing_id.date', '<=',
                     self.end_billing_date)]
        if self.start_billing_due_date:
            dom += [('purchase_billing_id.date_due', '>=',
                     self.start_billing_due_date)]
        if self.end_billing_due_date:
            dom += [('purchase_billing_id.date_due', '<=',
                     self.end_billing_due_date)]
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids.ids)]
        if self.billing_ids:
            dom += [('purchase_billing_id', 'in',
                     self.billing_ids.ids)]
        self.results = Result.search(dom, order="purchase_billing_id")
