from openerp import models, fields, api


class XLSXReportSupplierReceiptFollowUp(models.TransientModel):
    _name = 'xlsx.report.supplier.receipt.follow.up'
    _inherit = 'xlsx.report'

    # Search Criteria
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('supplier', '=', True)],
    )
    followup_receipt = fields.Selection(
        [('following', 'Following'),
         ('received', 'Received')],
        string='Receipt Followup',
        required=True,
    )
    # Report Result
    results = fields.Many2many(
        'account.voucher',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['account.voucher']
        dom = [('state', '=', 'posted')]
        if self.fiscalyear_id:
            dom += [('period_id.fiscalyear_id', '=', self.fiscalyear_id.id)]
        if self.partner_id:
            dom += [('partner_id', '=', self.partner_id.id)]
        if self.followup_receipt:
            dom += [('followup_receipt', '=', self.followup_receipt)]
        self.results = Result.search(dom)
