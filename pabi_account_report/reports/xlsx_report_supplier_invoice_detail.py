from openerp import models, fields, api


class XLSXReportSupplierInvoiceDetail(models.TransientModel):
    _name = 'xlsx.report.supplier.invoice.detail'
    _inherit = 'xlsx.report'

    # Search Criteria
    operating_unit_ids = fields.Many2many(
        'operating.unit',
        string='Operating Unit(s)',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Supplier(s)',
    )
    invoice_ids = fields.Many2many(
        'account.invoice',
        string='Invoice(s)',
        domain=[('state', 'in', ('open', 'paid')),
                ('type', 'in', ('in_invoice', 'in_refund'))],
    )
    open = fields.Boolean(
        string='Open Invoices',
        default=True,
    )
    paid = fields.Boolean(
        string='Paid Invoices',
        default=False,
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
        dom = [('type', 'in', ('in_invoice', 'in_refund'))]
        if self.operating_unit_ids:
            dom += [('operating_unit_id', 'in', self.operating_unit_ids.ids)]
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids.ids)]
        if self.invoice_ids:
            dom += [('id', 'in', self.invoice_ids.ids)]
        if self.open and self.paid:
            dom += [('state', 'in', ('open', 'paid'))]
        elif self.open:
            dom += [('state', '=', 'open')]
        elif self.paid:
            dom += [('state', '=', 'paid')]
        else:
            dom = [('id', '=', 0)]  # Don't show any invoices
        self.results = Result.search(dom)
