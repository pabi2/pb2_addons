# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
import time
import pandas as pd


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


class XLSXReportReceivableDetail(models.TransientModel):
    _name = 'xlsx.report.receivable.detail'
    _inherit = 'report.account.common'

    # Search Criteria
    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Customers',
    )
    as_of_date = fields.Date(
        string='As of Date',
    )
    period_length_days = fields.Integer(
        string='Period Length (days)',
        default=30,
        required=True,
    )
    move_ids = fields.Many2many(
        'account.move',
        string='Document Number(s)',
    )
    filter = fields.Selection(
        selection_add=[('filter_as_of_date', 'As of Date')],
    )
    date_start_real = fields.Date(
        string='Real Start Date',
        compute='_compute_date_real',
    )
    date_end_real = fields.Date(
        string='Real End Date',
        compute='_compute_date_real',
    )
    # Report Result
    results = fields.Many2many(
        'receivable.detail.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.onchange('filter')
    def _onchange_filter(self):
        super(XLSXReportReceivableDetail, self)._onchange_filter()
        self.as_of_date = False
        if self.filter == "filter_as_of_date":
            self.as_of_date = time.strftime('%Y-%m-%d')
            self.fiscalyear_start_id = self.fiscalyear_end_id = False

    @api.model
    def _get_date_list(self, date_start, date_end):
        return [x.strftime("%Y-%m-%d") for x in pd.date_range(date_start,
                                                              date_end)]

    @api.multi
    def _compute_date_real(self):
        self.ensure_one()
        Fiscalyear = self.env['account.fiscalyear']
        date_start = Fiscalyear.search(
            [('company_id', '=', self.company_id.id)],
            order="date_start", limit=1).date_start
        date_end = Fiscalyear.search(
            [('company_id', '=', self.company_id.id)],
            order="date_stop desc", limit=1).date_stop
        date_list = self._get_date_list(date_start, date_end)
        if self.fiscalyear_start_id:
            date_fiscalyear_start = self.fiscalyear_start_id.date_start
            temp_date_list = self._get_date_list(date_fiscalyear_start,
                                                 date_end)
            date_list = list(set(date_list) & set(temp_date_list))
        if self.fiscalyear_end_id:
            date_fiscalyear_end = self.fiscalyear_end_id.date_stop
            temp_date_list = self._get_date_list(date_start,
                                                 date_fiscalyear_end)
            date_list = list(set(date_list) & set(temp_date_list))
        if self.period_start_id:
            date_period_start = self.period_start_id.date_start
            temp_date_list = self._get_date_list(date_period_start, date_end)
            date_list = list(set(date_list) & set(temp_date_list))
        if self.period_end_id:
            date_period_end = self.period_end_id.date_stop
            temp_date_list = self._get_date_list(date_start, date_period_end)
            date_list = list(set(date_list) & set(temp_date_list))
        if self.date_start:
            temp_date_list = self._get_date_list(self.date_start, date_end)
            date_list = list(set(date_list) & set(temp_date_list))
        if self.date_end:
            temp_date_list = self._get_date_list(date_start, self.date_end)
            date_list = list(set(date_list) & set(temp_date_list))
        if self.as_of_date:
            temp_date_list = self._get_date_list(date_start, self.as_of_date)
            date_list = list(set(date_list) & set(temp_date_list))
        try:
            self.date_start_real = min(date_list)
            self.date_end_real = max(date_list)
        except Exception:
            self.date_start_real = self.date_end_real = False

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['receivable.detail.view']
        dom = []
        if self.account_ids:
            dom += [('invoice_move_line_id.account_id', 'in',
                     self.account_ids.ids)]
        if self.partner_ids:
            dom += [('invoice_move_line_id.partner_id', 'in',
                     self.partner_ids.ids)]
        if self.move_ids:
            dom += [('invoice_move_line_id.move_id', 'in', self.move_ids.ids)]
        if self.fiscalyear_start_id:
            dom += [('invoice_move_line_id.move_id.date', '>=',
                     self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('invoice_move_line_id.move_id.date', '<=',
                     self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('invoice_move_line_id.move_id.date', '>=',
                     self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('invoice_move_line_id.move_id.date', '<=',
                     self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('invoice_move_line_id.move_id.date', '>=',
                     self.date_start)]
        if self.date_end:
            dom += [('invoice_move_line_id.move_id.date', '<=',
                     self.date_end)]
        if self.as_of_date:
            dom += [('invoice_move_line_id.move_id.date', '<=',
                     self.as_of_date)]
        self.results = Result.search(dom)
