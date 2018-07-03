from openerp import models, fields, api, tools


class XLSXReportReceivableDetail(models.TransientModel):
    _name = 'xlsx.report.receivable.detail'
    _inherit = 'report.account.common'

    # Search Criteria
    start_doc_posting_date = fields.Date(
        string='Document Posting Date From',
    )
    end_doc_posting_date = fields.Date(
        string='Document Posting Date To',
    )
    start_doc_date = fields.Date(
        string='Document Date From',
    )
    end_doc_date = fields.Date(
        string='Document Date To',
    )
    system_ids = fields.Many2many(
        'interface.system',
        string='System Origin',
    )
    move_ids = fields.Many2many(
        'account.move',
        'xlsx_report_receivable_detail_move_rel',
        'report', 'move_id',
        string='Document Number(s)',
        domain=[('state', '=', 'posted'),
                ('doctype', 'in',
                ['out_invoice', 'out_refund', 'adjustment'])],
    )
    partner_ids = fields.Many2many(
        'res.partner',
        'xlsx_report_receivable_detail_partner_rel',
        'report_id', 'partner_id',
        string='Customers',
    )
    account_ids = fields.Many2many(
        'account.account',
        'xlsx_report_receivable_detail_account_rel',
        'report_id', 'account_id',
        string='Accounts',
        domain=[('type', '=', 'receivable')],
    )
    # Report Result
    results = fields.Many2many(
        'receivable.detail.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['receivable.detail.view']
        Fiscalyear = self.env['account.fiscalyear']
        date_start = \
            Fiscalyear.search([], order="date_start", limit=1).date_start
        date_end = \
            Fiscalyear.search([], order="date_stop desc", limit=1).date_stop
        if self.fiscalyear_start_id:
            date_start = self.fiscalyear_start_id.date_start
        if self.fiscalyear_end_id:
            date_end = self.fiscalyear_end_id.date_stop
        if self.period_start_id:
            date_start = self.period_start_id.date_start
        if self.period_end_id:
            date_end = self.period_end_id.date_stop
        if self.date_start:
            date_start = self.date_start
        if self.date_end:
            date_end = self.date_end
        dom = [('invoice_move_line_id.move_id.state', '=', 'posted'),
               ('invoice_move_line_id.invoice.date_due', '>=', date_start),
               ('invoice_move_line_id.invoice.date_due', '<=', date_end)]
        if self.partner_ids:
            dom += [('invoice_move_line_id.partner_id', 'in',
                    self.partner_ids.ids)]
        if self.account_ids:
            dom += [('invoice_move_line_id.account_id', 'in',
                    self.account_ids.ids)]
        if self.system_ids:
            dom += [('invoice_move_line_id.system_id', 'in',
                    self.system_ids.ids)]
        if self.move_ids:
            dom += [('invoice_move_line_id.move_id', 'in',
                    self.move_ids.ids)]
        self.results = Result.search(dom)


class ReceivableDetailView(models.Model):
    _name = 'receivable.detail.view'
    _auto = False

    invoice_move_line_id = fields.Many2one(
        'account.move.line',
        string='invoice move',
        readonly=True,
    )
    voucher_move_line_id = fields.Many2one(
        'account.move.line',
        string='voucher move',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY invoice_move_line_id,
                   voucher_move_line_id) AS id,
                   invoice_move_line_id, voucher_move_line_id
            FROM
            (
                (
                    SELECT invoice_line.move_line_id AS invoice_move_line_id,
                           voucher_line.move_line_id AS voucher_move_line_id
                    FROM
                    (
                        (
                            SELECT aml.id AS move_line_id,
                                   aml.reconcile_id, aml.reconcile_partial_id
                            FROM account_move_line aml
                            JOIN account_account aa ON aa.id = aml.account_id
                            AND aa.type = 'receivable'
                            JOIN interface_account_entry iae
                            ON aml.move_id = iae.move_id
                            WHERE iae.type = 'invoice'
                            OR aml.doctype = 'adjustment'
                        ) invoice_line
                        LEFT JOIN
                        (
                            SELECT aml.id AS move_line_id,
                                   aml.reconcile_id, aml.reconcile_partial_id
                            FROM account_move_line aml
                            JOIN account_account aa ON aa.id = aml.account_id
                            AND aa.type = 'receivable'
                            JOIN interface_account_entry iae
                            ON aml.move_id = iae.move_id
                            WHERE iae.type = 'voucher'
                        ) voucher_line
                        ON invoice_line.reconcile_id =
                           voucher_line.reconcile_id
                        OR invoice_line.reconcile_partial_id =
                           voucher_line.reconcile_partial_id
                    )
                )
                UNION
                (
                    SELECT invoice_line.move_line_id AS invoice_move_line_id,
                           voucher_line.move_line_id AS voucher_move_line_id
                    FROM
                    (
                        (
                            SELECT aml.id as move_line_id,
                                   aml.reconcile_id, aml.reconcile_partial_id
                            FROM account_move_line aml
                            JOIN account_account aa ON aa.id = aml.account_id
                            AND aa.type = 'receivable'
                            WHERE doctype in ('out_invoice',
                                'out_refund', 'adjustment')
                        ) invoice_line
                        LEFT JOIN
                        (
                            SELECT aml.id as move_line_id,
                            aml.reconcile_id, aml.reconcile_partial_id
                            FROM account_move_line aml
                            JOIN account_account aa ON aa.id = aml.account_id
                            AND aa.type = 'receivable'
                            WHERE doctype = 'receipt'
                        ) voucher_line
                            ON invoice_line.reconcile_id =
                                voucher_line.reconcile_id
                            OR invoice_line.reconcile_partial_id =
                                voucher_line.reconcile_partial_id
                    )
                )
            ) invoice_interface
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
