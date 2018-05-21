from openerp import models, fields, api


class XLSXReportChequeReport(models.TransientModel):
    _name = 'xlsx.report.cheque.register'
    _inherit = 'xlsx.report'

    # Search Criteria
    date_cheque_received = fields.Date(
        string='Cheque Received',
    )
    cheque_lot_ids = fields.Many2many(
        'cheque.lot',
        'xlsx_report_cheque_register_cheque_lot_rel',
        'report_id', 'lot_id',
        string='Lot Number(s)',
    )
    number_cheque_from = fields.Char(
        string='Cheque Number From',
    )
    number_cheque_to = fields.Char(
        string='Cheque Number To',
    )
    account_ids = fields.Many2many(
        'account.account',
        'xlsx_report_cheque_register_account_rel',
        'report_id', 'account_id',
        string='Account(s)',
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
        dom = [('state', 'in', ['posted', 'cancel']),
               ('payment_type', '=', 'cheque')]
        if self.date_cheque_received:
            dom += [('date_cheque_received', '=', self.date_cheque_received)]
        if self.cheque_lot_ids:
            dom += [('cheque_lot_id', 'in', self.cheque_lot_ids.ids)]
        if self.number_cheque_from:
            dom += [('number_cheque', '>=', self.number_cheque_from)]
        if self.number_cheque_to:
            dom += [('number_cheque', '<=', self.number_cheque_to)]
        if self.account_ids:
            dom += [('account_id', 'in', self.account_ids.ids)]
        self.results = Result.search(dom)
