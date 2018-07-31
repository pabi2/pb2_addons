# -*- coding: utf-8 -*-
from openerp import models, fields, api


class XLSXReportPayableBalance(models.TransientModel):
    _name = 'xlsx.report.payable.balance'
    _inherit = 'report.account.common'

    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
    )
    results = fields.Many2many(
        'account.move.line',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        """
        Solution
        1. Get from account move line
        2. Check doctype to supplier invoice, supplier refund and adjustment
        3. Check account type to payable
        4. Check state journal to posted
        5. Check reconcile to False
        """
        self.ensure_one()
        Result = self.env['account.move.line']
        dom = [('doctype', 'in', ['in_invoice', 'in_refund',
                                  'in_invoice_debitnote', 'adjustment']),
               ('account_id.type', '=', 'payable'),
               ('move_id.state', '=', 'posted'),
               ('reconcile_id', '=', False)]
        if self.account_ids:
            dom += [('account_id', 'in', self.account_ids.ids)]
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids.ids)]
        if self.fiscalyear_start_id:
            dom += [('move_id.date', '>=',
                     self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('move_id.date', '<=', self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('move_id.date', '>=', self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('move_id.date', '<=', self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('move_id.date', '>=', self.date_start)]
        if self.date_end:
            dom += [('move_id.date', '<=', self.date_end)]
        self.results = Result.search(dom, order="account_id,partner_id")
