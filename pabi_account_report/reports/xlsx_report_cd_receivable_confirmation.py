# -*- coding: utf-8 -*-
from openerp import models, fields, api


class XLSXReportCDReceivableConfirmation(models.TransientModel):
    _name = 'xlsx.report.cd.receivable.confirmation'
    _inherit = 'report.account.common'

    filter = fields.Selection(
        default='filter_date',
        readonly=True,
    )
    date_report = fields.Date(
        string='Report Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
    )
    bank_ids = fields.Many2many(
        'res.bank',
        string='Banks',
    )
    results = fields.Many2many(
        'pabi.common.loan.agreement.report.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        """
        Snap short
        1. State to bank paid
        2. Bank paid date <= Report date
        3. Sale order must confirm already
        4. Sale order date <= Report date
        5. Customer invoice not paid "OR"
           Customer invoice paid after report date
        7. Customer invoice not cancel "OR"
           Customer invoice cancel after report date
        """
        self.ensure_one()
        Result = self.env['pabi.common.loan.agreement.report.view']
        dom = []
        if self.partner_ids:
            dom += [('loan_agreement_id.borrower_partner_id', 'in',
                     self.partner_ids.ids)]
        if self.bank_ids:
            dom += [('loan_agreement_id.bank_id.bank', 'in',
                     self.bank_ids.ids)]
        # Check for snap short
        dom += [('loan_agreement_id.supplier_invoice_id.date_paid', '!=',
                 False),
                ('loan_agreement_id.supplier_invoice_id.date_paid', '<=',
                 self.date_report),
                ('order_id.date_confirm', '!=', False),
                ('order_id.date_confirm', '<=', self.date_report),
                '|', ('invoice_plan_id.ref_invoice_id.date_paid', '=', False),
                ('invoice_plan_id.ref_invoice_id.date_paid', '>',
                 self.date_report),
                '|', ('invoice_plan_id.ref_invoice_id.cancel_move_id', '=',
                      False),
                ('invoice_plan_id.ref_invoice_id.cancel_move_id.create_date',
                '>', self.date_report)]
        self.results = Result.search(dom)
