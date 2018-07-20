from openerp import models, fields, api, tools


class StatusChequeInventoryView(models.Model):
    _name = 'status.cheque.inventory.view'
    _auto = False

    account_voucher = fields.Many2one(
        'account.voucher',
        string='Account Voucher',
        readonly=True,
    )
    date_void = fields.Date(
        string='Date Void',
        readonly=True,
    )
    account_voucher_number = fields.Char(
        string='Number',
        readonly=True,
    )
    code = fields.Char(
        string='Code',
        readonly=True,
    )
    number_cheque = fields.Char(
        string='Number Cheque',
        readonly=True,
    )
    cheque_number = fields.Char(
        string='Cheque Number',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY av.id) AS id,
            av.id AS account_voucher , av.number AS account_voucher_number,
            cr.date_void AS date_void, aa.code, av.number_cheque,
            cr.number AS cheque_number
            FROM account_voucher av
            LEFT JOIN account_account aa ON av.account_id = aa.id
            LEFT JOIN cheque_lot cl ON av.cheque_lot_id = cl.id
            LEFT JOIN payment_export pe ON av.payment_export_id = pe.id
            LEFT JOIN cheque_register cr
            ON av.payment_export_id = cr.payment_export_id
            WHERE av.payment_type = 'cheque' AND av.state = 'posted'
            AND pe.state = 'done' AND av.date_cheque_received is not NULL
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportStatusChequeInventory(models.TransientModel):
    _name = 'xlsx.report.status.cheque.inventory'
    _inherit = 'report.account.common'

    account_ids = fields.Many2many(
        'account.account',
        'report_id', 'account_id',
        string='Accounts',
    )
    journal_ids = fields.Many2many(
        'account.journal',
        string='Journal',
    )
    filter = fields.Selection(
        default='filter_date',
        readonly=True,
    )
    cheque_lot_ids = fields.Many2many(
        'cheque.lot',
        string='Cheque Lot',
    )
    number_cheque_from = fields.Char(
        string='Cheque Number From',
    )
    number_cheque_to = fields.Char(
        string='Cheque Number To',
    )
    as_of_date = fields.Date(
        string='As of Date',
    )
    results = fields.Many2many(
        'status.cheque.inventory.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['status.cheque.inventory.view']
        dom = []
        if self.journal_ids:
            dom += [('account_voucher.journal_id', 'in', self.journal_ids.ids)]
        if self.cheque_lot_ids:
            dom += [('account_voucher.cheque_lot_id', 'in',
                    self.cheque_lot_ids.ids)]
        if self.as_of_date:
            dom += [('account_voucher.date_cheque', '<=', self.as_of_date)]
        if self.number_cheque_from:
            dom += [('cheque_number', '>=', self.number_cheque_from)]
        if self.number_cheque_to:
            dom += [('cheque_number', '<=', self.number_cheque_to)]
        self.results = Result.search(dom, order='code,number_cheque')
