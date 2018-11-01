# -*- coding: utf-8 -*-
from openerp import models, fields, api


class XLSXReportRevenueLedger(models.TransientModel):
    _name = 'xlsx.report.revenue.ledger'
    _inherit = 'report.account.common'

    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
    )
    chartfield_ids = fields.Many2many(
        'chartfield.view',
        string='Budget',
        domain=[('model', '!=', 'res.personnel.costcenter')],
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Customers',
    )
    results = fields.Many2many(
        'pabi.common.account.report.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        """
        Solution
        1. Get from pabi.common.account.report.view
        2. Check account type is revenue
        """
        self.ensure_one()
        Result = self.env['pabi.common.account.report.view']
        dom = [('account_id.user_type.code', '=', 'Revenue')]
        if self.account_ids:
            dom += [('account_id', 'in', self.account_ids.ids)]
        if self.chartfield_ids:
            budgets = []
            for chartfield in self.chartfield_ids:
                if chartfield.type == 'sc:':
                    chartfield_id = chartfield.id - 1000000
                elif chartfield.type == 'pj:':
                    chartfield_id = chartfield.id - 2000000
                elif chartfield.type == 'cp:':
                    chartfield_id = \
                        self.env['res.invest.construction.phase'] \
                        .browse(chartfield.id - 3000000) \
                        .invest_construction_id.id
                    chartfield.model = 'res.invest.construction'
                elif chartfield.type == 'ia:':
                    chartfield_id = chartfield.id - 4000000
                elif chartfield.type == 'pc:':
                    chartfield_id = chartfield.id - 5000000
                budgets.append('%s,%s' %
                               (chartfield.model.encode('utf-8'),
                                chartfield_id))
            operator = 'in'
            budgets = tuple(budgets)
            if len(budgets) == 1:
                operator = '='
                budgets = "\'" + budgets[0] + "\'"
            self._cr.execute("""
                select id from pabi_common_account_report_view
                where budget %s %s""" % (operator, str(budgets)))
            dom += [('id', 'in', map(lambda x: x[0], self._cr.fetchall()))]
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids.ids)]
        if self.fiscalyear_start_id:
            dom += [('invoice_posting_date',
                    '>=', self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('invoice_posting_date',
                    '<=', self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('invoice_posting_date', '>=',
                     self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('invoice_posting_date', '<=',
                     self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('invoice_posting_date', '>=', self.date_start)]
        if self.date_end:
            dom += [('invoice_posting_date', '<=', self.date_end)]
        self.results = Result.search(dom).sorted(
                       key=lambda l: (l.charge_type,
                                      l.account_id.code,
                                      l.activity_group_id.code,
                                      l.activity_id.code,
                                      l.period_id.fiscalyear_id.name,
                                      l.period_id.name))
