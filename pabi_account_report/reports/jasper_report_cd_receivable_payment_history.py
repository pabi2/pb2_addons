# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime
import time


class JasperReportCDReceivablePaymentHistory(models.TransientModel):
    _name = 'jasper.report.cd.receivable.payment.history'
    _inherit = 'report.account.common'

    filter = fields.Selection(
        readonly=True,
        default='filter_date',
    )
    date_report = fields.Date(
        string='Report Date',
        required=True,
        readonly=True,
        default=lambda self: fields.Date.context_today(self),
    )
    bank_id = fields.Many2one(
        'res.bank',
        string='Bank',
    )
    bank_branch_id = fields.Many2one(
        'res.bank.branch',
        string='Bank Branch'
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Customers',
    )

    @api.onchange('bank_id')
    def _onchange_bank_id(self):
        self.bank_branch_id = False
        self.partner_ids = False

    @api.multi
    def _get_report_name(self):
        self.ensure_one()
        report_name = "cd_receivable_payment_history_group_by_customer"
        if len(self.bank_id):
            report_name = "cd_receivable_payment_history_group_by_bank"
        return report_name

    @api.multi
    def _get_domain(self):
        """
        Solution
        1. Bank invoice must paid
        2. Sale order not in (draft, cancel)
        """
        self.ensure_one()
        dom = [('loan_agreement_id.supplier_invoice_id.date_paid', '!=',
                False),
               ('loan_agreement_id.sale_id.state',
                'not in', ('draft', 'cancel'))]
        if self.partner_ids:
            dom += [('loan_agreement_id.borrower_partner_id', 'in',
                     self.partner_ids.ids)]
        if self.bank_id:
            dom += [('loan_agreement_id.bank_id.bank', '=',
                     self.bank_id.id)]
        if self.bank_branch_id:
            dom += [('loan_agreement_id.bank_id.bank_branch', '=',
                     self.bank_branch_id.id)]
        return dom

    @api.multi
    def _get_datas(self):
        self.ensure_one()
        data = {'parameters': {}}
        dom = self._get_domain()
        data['ids'] = \
            self.env['pabi.common.loan.agreement.report.view'].search(dom).ids
        date_report = datetime.strptime(self.date_report, '%Y-%m-%d')
        data['parameters']['date_report'] = date_report.strftime('%d/%m/%Y')
        data['parameters']['user'] = self.env.user.display_name
        data['parameters']['date_run'] = time.strftime('%d/%m/%Y')
        return data

    @api.multi
    def run_report(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.report.xml',
            'report_name': self._get_report_name(),
            'datas': self._get_datas(),
        }
