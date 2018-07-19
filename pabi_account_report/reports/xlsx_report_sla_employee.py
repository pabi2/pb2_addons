# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools


class SLAEmployeeView(models.Model):
    _name = 'sla.employee.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        readonly=True,
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        string='Voucher',
        readonly=True,
    )
    voucher_line_id = fields.Many2one(
        'account.voucher.line',
        string='Voucher Line',
        readonly=True,
    )
    export_id = fields.Many2one(
        'payment.export',
        string='Export',
        readonly=True,
    )
    date_invoice = fields.Date(
        string='Posting Date',
        readonly=True,
    )
    invoice_number = fields.Char(
        string='Invoice Number',
        readonly=True
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY av.id) AS id,
                   inv.id AS invoice_id,
                   av.id AS voucher_id,
                   av_line.id AS voucher_line_id,
                   exp.id AS export_id,
                   inv.date_invoice,
                   inv.number AS invoice_number
            FROM account_voucher av
            LEFT JOIN account_voucher_line av_line ON
                av.id = av_line.voucher_id
            LEFT JOIN account_move_line am_line ON
                av_line.move_line_id = am_line.id
            LEFT JOIN account_invoice inv ON am_line.move_id = inv.move_id
            LEFT JOIN payment_export_line exp_line ON
                av.id = exp_line.voucher_id
            LEFT JOIN payment_export exp ON exp_line.export_id = exp.id
            WHERE av.type = 'payment' AND av.state = 'posted' AND
                exp.state = 'done' AND
                SPLIT_PART(inv.source_document_id, ',', 1)
                = 'hr.expense.expense'
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportSLAEmployee(models.TransientModel):
    _name = 'xlsx.report.sla.employee'
    _inherit = 'report.account.common'

    user_ids = fields.Many2many(
        'res.users',
        string='Validated By',
    )
    source_document_type = fields.Selection(
        [('expense', 'Expense'),
         ('advance', 'Advance')],
        string='Source Document Ref.',
    )
    results = fields.Many2many(
        'sla.employee.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['sla.employee.view']
        dom = []

        if self.user_ids:
            dom += [('voucher_id.create_uid', 'in', self.user_ids.ids)]
        if self.source_document_type:
            dom += [('invoice_id.source_document_type', '=',
                     self.source_document_type != 'nothing' and
                     self.source_document_type or False)]
        if self.fiscalyear_start_id:
            dom += [('voucher_id.date', '>=',
                     self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('voucher_id.date', '<=',
                     self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('voucher_id.date', '>=',
                     self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('voucher_id.date', '<=',
                     self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('voucher_id.date', '>=', self.date_start)]
        if self.date_end:
            dom += [('voucher_id.date', '<=', self.date_end)]
        self.results = Result.search(dom, order="date_invoice,invoice_number")
