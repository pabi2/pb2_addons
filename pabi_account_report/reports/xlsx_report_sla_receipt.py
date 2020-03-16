# -*- coding: utf-8 -*-
from openerp import models, fields, api
import datetime
import numpy as np


class AccountBankReceiptView(models.AbstractModel):
    _name = 'account.bank.receipt.view'
    _inherit = 'account.bank.receipt'

    business_day = fields.Integer(
        string='Business Day',
        compute='_compute_business_day',
    )

    @api.multi
    def _compute_business_day(self):
        holidays = self.env['calendar.event'].search(
            [('user_id.login', '=', 'holiday')]).mapped('start_date')
        for rec in self:
            date_start = rec.date_accept
            date_end = rec.receipt_date
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


class XLSXReportSLAReceipt(models.TransientModel):
    _name = 'xlsx.report.sla.receipt'
    _inherit = 'report.account.common'

    user_ids = fields.Many2many(
        'res.users',
        string='Validated By',
    )
    results = fields.Many2many(
        'account.bank.receipt.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
    async_process = fields.Boolean(
        string='Run task in background?',
        default=True,
    )

    @api.model
    def _domain_to_where_str(self, domain):
        """ Helper Function for better performance """
        where_dom = [" %s %s %s " % (x[0], x[1], isinstance(x[2], basestring)
                     and "'%s'" % x[2] or x[2]) for x in domain]

        where_str = 'and'.join(where_dom)
        where_str = where_str.replace(',)', ')')
        return where_str

    @api.multi
    def _compute_results(self):
        """
        Solution
        1. Get from account bank receipt
        2. Check state is done
        """
        self.ensure_one()
        Result = self.env['account.bank.receipt.view']
        dom = [('abr.state', '=', 'done')]
        if self.user_ids:
            dom += [('abr.validate_user_id', 'in', self.user_ids.ids)]
        if self.fiscalyear_start_id:
            dom += [('am.date', '>=',
                     self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('am.date', '<=', self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('am.date', '>=', self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('am.date', '<=', self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('am.date', '>=', self.date_start)]
        if self.date_end:
            dom += [('am.date', '<=', self.date_end)]

        where_str = self._domain_to_where_str(dom)

        self._cr.execute("""
            select abr.*
            from account_bank_receipt abr
                left join account_move am on am.id = abr.move_id
            where %s
            """ % (where_str))

        sla_receipt = self._cr.dictfetchall()
        self.results = [Result.new(line).id for line in sla_receipt]

        # self.results = Result.search(dom, order="name")
