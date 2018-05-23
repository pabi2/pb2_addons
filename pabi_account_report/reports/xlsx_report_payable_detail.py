from openerp import models, fields, api, tools


class PayableDetailView(models.Model):
    _name = 'payable.detail.view'
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
                       WHERE doctype = 'payment') l2 ON
                r.id = l2.reconcile_id OR r.id = l2.reconcile_partial_id
            LEFT JOIN account_voucher av ON l2.move_id = av.move_id
            LEFT JOIN (SELECT * FROM payment_export_line l3
                       LEFT JOIN payment_export exp ON l3.export_id = exp.id
                       WHERE exp.state = 'done') exp_line ON
                av.id = exp_line.voucher_id
            LEFT JOIN account_voucher_tax tax ON inv.id = tax.invoice_id
                AND tax.voucher_id = av.id AND tax.tax_code_type = 'wht'
            WHERE l.doctype IN ('in_invoice', 'in_refund', 'adjustment') AND
                l.account_id = inv.account_id
            ORDER BY l.partner_id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportPayableDetail(models.TransientModel):
    _name = 'xlsx.report.payable.detail'
    _inherit = 'xlsx.report'

    # Search Criteria
    account_ids = fields.Many2many(
        'account.account',
        'xlsx_report_partner_detail_account_rel',
        'report_id', 'account_id',
        string='Account(s)',
        domain=[('type', '=', 'payable')],
        required=True,
    )
    partner_ids = fields.Many2many(
        'res.partner',
        'xlsx_report_payable_detail_partner_rel',
        'report_id', 'partner_id',
        string='Supplier(s)',
        domain=[('supplier', '=', True)],
    )
    start_fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year From',
    )
    end_fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year To',
    )
    start_period_id = fields.Many2one(
        'account.period',
        string='Period From',
        domain=[('special', '=', False), ('state', '=', 'draft')],
    )
    end_period_id = fields.Many2one(
        'account.period',
        string='Period To',
        domain=[('special', '=', False), ('state', '=', 'draft')],
    )
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
    move_ids = fields.Many2many(
        'account.move',
        'xlsx_report_payable_detail_move_rel',
        'report', 'move_id',
        string='Document Number(s)',
        domain=[('state', '=', 'posted'),
                ('doctype', 'in', ['in_invoice', 'in_refund', 'adjustment'])],
    )
    # Report Result
    results = fields.Many2many(
        'payable.detail.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['payable.detail.view']
        dom = [('move_line_id.account_id', 'in', self.account_ids.ids)]
        if self.partner_ids:
            dom += [('move_line_id.partner_id', 'in', self.partner_ids.ids)]
        if self.start_fiscalyear_id:
            dom += [('move_line_id.period_id.fiscalyear_id.date_start', '>=',
                     self.start_fiscalyear_id.date_start)]
        if self.end_fiscalyear_id:
            dom += [('move_line_id.period_id.fiscalyear_id.date_start', '<=',
                     self.end_fiscalyear_id.date_start)]
        if self.start_period_id:
            dom += [('move_line_id.period_id.date_start', '>=',
                     self.start_period_id.date_start)]
        if self.end_period_id:
            dom += [('move_line_id.period_id.date_start', '<=',
                     self.end_period_id.date_start)]
        if self.start_doc_posting_date:
            dom += [('move_line_id.move_id.date', '>=',
                     self.start_doc_posting_date)]
        if self.end_doc_posting_date:
            dom += [('move_line_id.move_id.date', '<=',
                     self.end_doc_posting_date)]
        if self.start_doc_date:
            dom += [('move_line_id.move_id.date_document', '>=',
                     self.start_doc_date)]
        if self.end_doc_date:
            dom += [('move_line_id.move_id.date_document', '<=',
                     self.end_doc_date)]
        if self.move_ids:
            dom += [('move_line_id.move_id', 'in', self.move_ids.ids)]
        self.results = Result.search(dom)
