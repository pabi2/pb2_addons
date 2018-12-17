# -*- coding: utf-8 -*-
from openerp import models, fields, api


class XLSXReportAdvancePayment(models.TransientModel):
    _name = 'xlsx.report.advance.payment'
    _inherit = 'report.account.common'

    filter = fields.Selection(
        readonly=True,
        default='filter_date',
    )
    date_report = fields.Date(
        string='As of Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
        domain=lambda self: self._get_domain_account_ids(),
    )
    results = fields.Many2many(
        'account.move.line',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.model
    def _get_account_ids(self):
        return self.env.user.company_id.other_deposit_account_ids.ids

    @api.model
    def _get_domain_account_ids(self):
        return [('id', 'in', self._get_account_ids())]

    @api.multi
    def _compute_results(self):
        """
        Solution
        1. Get from account.move.line
        2. Check account code from Other Advance Accounts in PABI Apps
           (Settings > Configuration > PABI Apps)
        3. Check invoice to advance
        4. Check reconcile is False
        """
        self.ensure_one()
        Result = self.env["account.move.line"]
        dom = [('account_id', 'in', self._get_account_ids()),
               # ('invoice.is_advance', '=', True),
               ('reconcile_id', '=', False)]
        if self.account_ids:
            dom += [('account_id', 'in', self.account_ids.ids)]
        self.results = Result.search(dom)
