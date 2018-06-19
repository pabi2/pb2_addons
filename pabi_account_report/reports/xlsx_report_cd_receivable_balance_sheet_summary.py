# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools


class XLSXReportCDReceivableBalanceSheetSummary(models.TransientModel):
    _name = 'xlsx.report.cd.receivable.balance.sheet.summary'
    _inherit = 'report.account.common'

    partner_ids = fields.Many2many(
        'res.partner',
        'cd_receivable_balance_sheet_summary_partner_rel',
        'report_id', 'partner_id',
        string='Customers',
    )
    mou_ids = fields.Many2many(
        'loan.bank.mou',
        'cd_receivable_balance_sheet_summary_mou_rel',
        'report_id', 'mou_id',
        string='MOU',
    )
    account_ids = fields.Many2many(
        'account.account',
        'cd_receivable_balance_sheet_summary_account_rel',
        'report_id', 'account_id',
        string='Accounts',
        default=lambda self: self.env['account.account'].search(
            [('code', '=', '1102010006')]),
        readonly=True,
    )
    balance_sheet_summary_results = fields.Many2many(
        'loan.customer.agreement',
        string='Balance Sheet Summary Results',
        compute='_compute_balance_sheet_summary_results',
        help='Use compute fields, so there is nothing store in database',
    )
    brought_forward_results = fields.Many2many(
        'loan.customer.agreement.view',
        string='Brought Forward Results',
        compute='_compute_brought_forward_results',
        help='Use compute fields, so there is nothing store in database',
    )
    receipt_results = fields.Many2many(
        'loan.customer.agreement.view',
        string='Receipt Results',
        compute='_compute_receipt_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_balance_sheet_summary_results(self):
        self.ensure_one()
        Result = self.env['loan.customer.agreement']
        dom = [('sale_id.state', 'not in', ('draft', 'cancel'))]
        if self.partner_ids:
            dom += [('borrower_partner_id', 'in', self.partner_ids.ids)]
        if self.mou_ids:
            dom += [('mou_id', 'in', self.mou_ids.ids)]
        if self.account_ids:
            dom += [('account_receivable_id', 'in', self.account_ids.ids)]
        self.balance_sheet_summary_results = \
            Result.search(dom, order="borrower_partner_id,mou_id,sale_id,name")

    @api.multi
    def _compute_brought_forward_results(self):
        self.ensure_one()
        Result = self.env['loan.customer.agreement.view']
        Fiscalyear = self.env['account.fiscalyear']
        date_start = \
            Fiscalyear.search([], order="date_start", limit=1).date_start
        if self.fiscalyear_start_id:
            date_start = self.fiscalyear_start_id.date_start
        if self.period_start_id:
            date_start = self.period_start_id.date_start
        if self.date_start:
            date_start = self.date_start
        dom = [('loan_agreement_id.sale_id.state', 'not in',
                ('draft', 'cancel')),
               ('invoice_id.state', '=', 'paid'),
               ('invoice_id.date_due', '<', date_start)]
        if self.partner_ids:
            dom += [('loan_agreement_id.borrower_partner_id', 'in',
                     self.partner_ids.ids)]
        if self.mou_ids:
            dom += [('loan_agreement_id.mou_id', 'in', self.mou_ids.ids)]
        if self.account_ids:
            dom += [('loan_agreement_id.account_receivable_id', 'in',
                     self.account_ids.ids)]
        self.brought_forward_results = Result.search(
            dom, order="loan_agreement_id")

    @api.multi
    def _compute_receipt_results(self):
        self.ensure_one()
        Result = self.env['loan.customer.agreement.view']
        Fiscalyear = self.env['account.fiscalyear']
        date_start = \
            Fiscalyear.search([], order="date_start", limit=1).date_start
        date_end = \
            Fiscalyear.search([], order="date_stop desc", limit=1).date_stop
        if self.fiscalyear_start_id:
            date_start = self.fiscalyear_start_id.date_start
        if self.fiscalyear_end_id:
            date_end = self.fiscalyear_end_id.date_stop
        if self.period_start_id:
            date_start = self.period_id.date_start
        if self.period_end_id:
            date_end = self.period_end_id.date_stop
        if self.date_start:
            date_start = self.date_start
        if self.date_end:
            date_end = self.date_end
        dom = [('loan_agreement_id.sale_id.state', 'not in',
                ('draft', 'cancel')),
               ('invoice_id.state', '=', 'paid'),
               ('invoice_id.date_due', '>=', date_start),
               ('invoice_id.date_due', '<=', date_end)]
        if self.partner_ids:
            dom += [('loan_agreement_id.borrower_partner_id', 'in',
                     self.partner_ids.ids)]
        if self.mou_ids:
            dom += [('loan_agreement_id.mou_id', 'in', self.mou_ids.ids)]
        if self.account_ids:
            dom += [('loan_agreement_id.account_receivable_id', 'in',
                     self.account_ids.ids)]
        self.receipt_results = Result.search(dom, order="loan_agreement_id")


class LoanCustomerAgreementView(models.Model):
    _name = 'loan.customer.agreement.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    loan_agreement_id = fields.Many2one(
        'loan.customer.agreement',
        string='Loan Agreement',
        readonly=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY lca.id, inv.id) AS id,
                   lca.id AS loan_agreement_id,
                   inv.id AS invoice_id
            FROM loan_customer_agreement lca
            LEFT JOIN account_invoice inv ON lca.id = inv.loan_agreement_id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
