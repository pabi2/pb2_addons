# -*- coding: utf-8 -*
from openerp import models, fields, api, tools


class XLSXReportSLAPurchase(models.TransientModel):
    _name = 'xlsx.report.sla.purchase'
    _inherit = 'report.account.common'

    user_ids = fields.Many2many(
        'res.users',
        string='Responsible',
    )
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
        if self.user_ids:
            dom += [('voucher_id.create_uid', 'in', self.user_ids.ids)]
        if self.fiscalyear_start_id:
            dom += [('voucher_id.period_id.fiscalyear_id.date_start', '>=',
                     self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('voucher_id.period_id.fiscalyear_id.date_stop', '<=',
                     self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('voucher_id.period_id.date_start', '>=',
                     self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('voucher_id.period_id.date_stop', '<=',
                     self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('voucher_id.date_value', '>=', self.date_start)]
        if self.date_end:
            dom += [('voucher_id.date_value', '<=', self.date_end)]
        self.results = Result.search(dom, order="fiscalyear,voucher_number")


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
    export_id = fields.Many2one(
        'payment.export',
        readonly=True,
    )
    date_due = fields.Date(
        string='Date Due',
        readonly=True,
    )
    fiscalyear = fields.Char(
        string='Fiscal Year',
        readonly=True,
    )
    voucher_number = fields.Char(
        string='Voucher Number',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY av.id) AS id,
                   av.id AS voucher_id,
                   COUNT(inv.id) AS count_invoice,
                   exp.id AS export_id,
                   MIN(inv.date_due) AS date_due,
                   af.name AS fiscalyear,
                   av.number AS voucher_number
            FROM account_voucher av
            LEFT JOIN account_voucher_line av_line ON
                av.id = av_line.voucher_id
            LEFT JOIN account_move_line am_line ON
                av_line.move_line_id = am_line.id
            LEFT JOIN account_invoice inv ON am_line.move_id = inv.move_id
            LEFT JOIN (SELECT pe.id, pel.voucher_id
                       FROM payment_export pe
                       LEFT JOIN payment_export_line pel ON
                        pe.id = pel.export_id
                       WHERE pe.state = 'done') exp ON av.id = exp.voucher_id
            LEFT JOIN account_period ap ON av.period_id = ap.id
            LEFT JOIN account_fiscalyear af ON ap.fiscalyear_id = af.id
            WHERE av.type = 'payment' AND av.state = 'posted' AND
                SPLIT_PART(inv.source_document_id, ',', 1) = 'purchase.order'
            GROUP BY av.id, exp.id, af.id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
