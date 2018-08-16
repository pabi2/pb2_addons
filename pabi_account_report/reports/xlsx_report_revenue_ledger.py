# -*- coding: utf-8 -*-
from openerp import models, fields, api


class XLSXReportRevenueLedger(models.TransientModel):
    _name = 'xlsx.report.revenue.ledger'
    _inherit = 'report.account.common'

    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
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
                       key=lambda l: (l.account_id.code,
                                      l.activity_group_id.code,
                                      l.activity_id.code,
                                      l.period_id.fiscalyear_id.name,
                                      l.period_id.name))
