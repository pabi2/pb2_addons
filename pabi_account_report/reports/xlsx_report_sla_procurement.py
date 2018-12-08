# -*- coding: utf-8 -*-
from openerp import models, fields, api
import datetime
import numpy as np


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    business_day = fields.Integer(
        string='Business Day',
        compute='_compute_business_day',
    )

    @api.multi
    def _compute_business_day(self):
        holidays = self.env['calendar.event'].search(
            [('user_id.login', '=', 'holiday')]).mapped('start_date')
        for rec in self:
            date_start = rec.date_receipt_billing
            date_end = rec.date_invoice
            if date_start and date_end:
                if date_end >= date_start:
                    date_end = (datetime.datetime.strptime(
                                date_end, '%Y-%m-%d')
                                + datetime.timedelta(days=1)) \
                                .strftime('%Y-%m-%d')
                else:
                    date_start = (datetime.datetime.strptime(
                                  date_start, '%Y-%m-%d')
                                  + datetime.timedelta(days=1)) \
                                  .strftime('%Y-%m-%d')
                rec.business_day = np.busday_count(
                    date_start, date_end, holidays=holidays)


class XLSXReportSLAProcurement(models.TransientModel):
    _name = 'xlsx.report.sla.procurement'
    _inherit = 'report.account.common'

    user_ids = fields.Many2many(
        'res.users',
        string='Validated By',
    )
    results = fields.Many2many(
        'account.invoice',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        """
        Solution
        1. Get from account invoice as state in ('open', 'paid')
        """
        self.ensure_one()
        Result = self.env['account.invoice']
        dom = [('state', 'in', ['open', 'paid']),
               ('type', 'in', ['in_invoice', 'in_refund'])]
        if self.user_ids:
            dom += [('validate_user_id', 'in', self.user_ids.ids)]
        if self.fiscalyear_start_id:
            dom += [('date_invoice', '>=',
                     self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('date_invoice', '<=',
                     self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('date_invoice', '>=',
                     self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('date_invoice', '<=', self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('date_invoice', '>=', self.date_start)]
        if self.date_end:
            dom += [('date_invoice', '<=', self.date_end)]
        self.results = Result.search(dom, order="number")
