from openerp import models, fields, api, tools


class ReceivableDetailView(models.Model):
    _name = 'receivable.detail.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Move Line',
        readonly=True,
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        string='Voucher',
        readonly=True,
    )
    export_id = fields.Many2one(
        'payment.export',
        string='Export',
        readonly=True,
    )
    purchase_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        readonly=True,
    )
    tax_id = fields.Many2one(
        'account.voucher.tax',
        string='Tax',
        readonly=True,
    )
    # loan_agreement_id = fields.Many2one(
    #     'receivable.detail.view',
    #     string='Loan Agreement',
    #     readonly=True,
    # )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY av.id) AS id,
                l.id AS move_line_id, av.id AS voucher_id, exp_line.export_id,
                po.id AS purchase_id, tax.id AS tax_id
            FROM account_move_line l
            LEFT JOIN account_invoice inv ON l.move_id = inv.move_id OR
                l.move_id = inv.cancel_move_id OR
                l.move_id = inv.adjust_move_id
            LEFT JOIN purchase_invoice_rel rel ON inv.id = rel.invoice_id
            LEFT JOIN purchase_order po ON rel.purchase_id = po.id
            LEFT JOIN account_move_reconcile r ON l.reconcile_id = r.id
                OR l.reconcile_partial_id = r.id
            LEFT JOIN (SELECT * FROM account_move_line
                       WHERE doctype = 'receipt') l2 ON
                r.id = l2.reconcile_id OR r.id = l2.reconcile_partial_id
            LEFT JOIN account_voucher av ON l2.move_id = av.move_id
            LEFT JOIN (SELECT * FROM payment_export_line l3
                       LEFT JOIN payment_export exp ON l3.export_id = exp.id
                       WHERE exp.state = 'done') exp_line ON
                av.id = exp_line.voucher_id
            LEFT JOIN account_voucher_tax tax ON inv.id = tax.invoice_id
                AND tax.voucher_id = av.id AND tax.tax_code_type = 'wht'
            WHERE l.doctype IN ('out_invoice', 'out_refund', 'adjustment') AND
                l.account_id = inv.account_id
            ORDER BY l.partner_id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


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
                ('doctype', 'in', ['out_invoice', 'out_refund', 'adjustment'])],
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
        dom = [('move_line_id.move_id.state','=','posted'),
               ('move_line_id.invoice.date_due', '>=', date_start),
               ('move_line_id.invoice.date_due', '<=', date_end)]
        if self.partner_ids:
            dom += [('move_line_id.partner_id', 'in', self.partner_ids.ids)]
        if self.account_ids:
            dom = [('move_line_id.account_id', 'in', self.account_ids.ids)]
        if self.system_ids:
            dom += [('move_line_id.system_id', 'in', self.system_ids.ids)]
        if self.move_ids:
            dom += [('move_line_id.move_id', 'in', self.move_ids.ids)]
        self.results = Result.search(dom)
