from openerp import models, fields, api


class XLSXReportChequeRegisterReport(models.TransientModel):
    _name = 'xlsx.report.cheque.register'
    _inherit = 'report.account.common'

    fiscalyear_ids = fields.Many2many(
        default=False,
    )
    date_from = fields.Date(
        default=False,
    )
    date_to = fields.Date(
        default=False,
    )
    filter = fields.Selection(
        [('filter_date', 'Date')],
        string='Filter by',
        required=True,
        default='filter_date',
    )
    date_cheque_received = fields.Date(
        string='Cheque Received Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    journal_ids = fields.Many2many(
        'account.journal',
        string='Payment Method(s)',
        domain=[('type', '=', 'bank'), ('intransit', '=', False)],
    )
    cheque_lot_ids = fields.Many2many(
        'cheque.lot',
        string='Lot Number(s)',
    )
    number_cheque_from = fields.Char(
        string='Cheque Number From',
    )
    number_cheque_to = fields.Char(
        string='Cheque Number To',
    )
    # Report Result
    results = fields.Many2many(
        'cheque.register',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['cheque.register']
        dom = []
        if self.date_cheque_received:
            dom += [('voucher_id.date_cheque_received', '=',
                     self.date_cheque_received)]
        if self.journal_ids:
            dom += [('journal_id', 'in', self.journal_ids.ids)]
        if self.cheque_lot_ids:
            dom += [('cheque_lot_id', 'in', self.cheque_lot_ids.ids)]
        if self.number_cheque_from:
            dom += [('number', '>=', self.number_cheque_from)]
        if self.number_cheque_to:
            dom += [('number', '<=', self.number_cheque_to)]
        self.results = Result.search(dom, order="journal_id,number")
