# -*- coding: utf-8 -*-
from openerp import models, fields, api
import datetime
import time
import pandas as pd
import re


class XLSXReportReceivableDetail(models.TransientModel):
    _name = 'xlsx.report.receivable.detail'
    _inherit = 'report.account.common'

    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
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
        string='Document Numbers',
    )
    system_ids = fields.Many2many(
        'interface.system',
        string='System Origin',
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
    line_filter_document = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    results = fields.Many2many(
        'account.move.line',
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
        Moveline = self.env['account.move.line']
        dom = [('account_id.type', '=', 'receivable'),
               ('move_id.state', '=', 'posted'),]
               #('date_maturity', '!=', False),]
        if self.account_ids:
            dom += [('account_id', 'in', self.account_ids.ids)]
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids.ids)]
        if self.move_ids:
            dom += [('move_id', 'in', self.move_ids.ids)]
        if self.system_ids:
            dom += [('system_id', 'in', self.system_ids.ids)]
        if self.fiscalyear_start_id:
            dom += [('date', '>=', self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('date', '<=', self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('date', '>=', self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('date', '<=', self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('date', '>=', self.date_start)]
        if self.date_end:
            dom += [('date', '<=', self.date_end)]
        if self.as_of_date:
            dom += [('date', '<=', self.as_of_date)]
        res_ids = []
        for x in Moveline.search(dom):
            res_ids += [x.id if x.move_id.doctype == 'adjustment' or x.date_maturity else False]
        res_ids = list(filter(lambda l: l != False, res_ids))
        self.results = Moveline.search([('id', 'in', res_ids)]).sorted(
            key=lambda l: (l.partner_id.search_key, l.date, l.move_id.name))

    @api.onchange('line_filter_document')
    def _onchange_line_filter_document(self):
        self.move_ids = []
        account_move = self.env['account.move']
        dom = [('company_id', '=', self.company_id.id), ('state', '=', 'posted'), ('doctype', 'in', ['out_invoice', 'out_refund', 'adjustment'])]
        if self.line_filter_document:
            names = self.line_filter_document.split('\n')
            names = [x.strip() for x in names]
            names = ','.join(names)
            dom.append(('name', 'ilike', names))
            self.move_ids = account_move.search(dom, order='id')