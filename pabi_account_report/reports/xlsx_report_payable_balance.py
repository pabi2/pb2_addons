from openerp import models, fields, api


class XLSXReportPayableBalance(models.TransientModel):
    _name = 'xlsx.report.payable.balance'
    _inherit = 'xlsx.report'

    # Search Criteria
    partner_ids = fields.Many2many(
        'res.partner',
        'xlsx_report_payable_balance_partner_rel',
        'report_id', 'partner_id',
        string='Supplier(s)',
        domain=[('supplier', '=', True)],
    )
    account_ids = fields.Many2many(
        'account.account',
        'xlsx_report_payable_balance_account_rel',
        'report_id', 'account_id',
        string='Account(s)',
        domain=[('type', '=', 'payable')],
        required=True,
    )
    # Report Result
    results = fields.Many2many(
        'account.move.line',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['account.move.line']
        dom = [('move_id.state', '=', 'posted'),
               ('reconcile_id', '=', False),
               ('doctype', 'in',
                ['in_invoice', 'in_refund', 'in_invoice_debitnote',
                 'adjustment']),
               ('account_id', 'in', self.account_ids.ids), ]
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids.ids)]
        self.results = Result.search(dom, order="account_id,partner_id")
