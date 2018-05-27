from openerp import models, fields, api, tools


class SLAPurchaseView(models.Model):
    _name = 'sla.purchase.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        readonly=True,
    )
    count_invoice = fields.Integer(
        string='Count Invoice',
        readonly=True,
    )
    export_name = fields.Char(
        string='Export Name',
        readonly=True,
    )
    date_due = fields.Date(
        string='Date Due',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY av.id) AS id,
                   av.id AS voucher_id, COUNT(inv.id) AS count_invoice,
                   STRING_AGG(exp_line.name, ', ' ORDER BY exp_line.name)
                    AS export_name, MIN(inv.date_due) AS date_due
            FROM account_move_line l
            LEFT JOIN account_invoice inv ON l.move_id = inv.move_id
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
            WHERE l.doctype IN ('in_invoice', 'in_refund') AND
                l.account_id = inv.account_id AND
                    SPLIT_PART(inv.source_document_id, ',', 1)
                        = 'purchase.order' AND av.id IS NOT NULL AND
                    av.state = 'posted'
            GROUP BY av.id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportSLAPurchase(models.TransientModel):
    _name = 'xlsx.report.sla.purchase'
    _inherit = 'xlsx.report'

    # Search Criteria
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
    user_ids = fields.Many2many(
        'res.users',
        'xlsx_report_sla_purchase_user_rel',
        'report_id', 'user_id',
        string='Responsible By',
    )
    # Report Result
    results = fields.Many2many(
        'sla.purchase.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['sla.purchase.view']
        dom = []
        if self.start_period_id:
            dom += [('voucher_id.period_id.date_start', '>=',
                     self.start_period_id.date_start)]
        if self.end_period_id:
            dom += [('voucher_id.period_id.date_start', '<=',
                     self.end_period_id.date_start)]
        if self.user_ids:
            dom += [('voucher_id.create_uid', 'in', self.user_ids.ids)]
        self.results = Result.search(dom)
