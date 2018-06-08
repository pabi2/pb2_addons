# -*- coding: utf-8 -*
from openerp import models, fields, api, tools
from datetime import datetime
import time


class JasperReportPaymentHistory(models.TransientModel):
    _name = 'jasper.report.payment.history'
    _inherit = 'report.account.common'

    fiscalyear_start_id = fields.Many2one(
        default=False,
    )
    fiscalyear_end_id = fields.Many2one(
        default=False,
    )
    filter = fields.Selection(
        readonly=True,
        default='filter_date',
    )
    date_report = fields.Date(
        string='Report Date',
        required=True,
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
        domain="[('customer', '=', True)]",
    )

    @api.onchange('bank_id')
    def _onchange_bank_id(self):
        self.bank_branch_id = False
        self.partner_ids = False

    @api.multi
    def _get_report_name(self):
        self.ensure_one()
        report_name = "customer_payment_history"
        if len(self.bank_id):
            report_name = "bank_payment_history"
        return report_name

    @api.multi
    def _get_datas(self):
        self.ensure_one()
        data = {'parameters': {}}
        dom = [('payment_id.move_id.create_date', '<=', self.date_report)]
        if self.partner_ids:
            dom += [('loan_agreement_id.borrower_partner_id', 'in',
                     self.partner_ids.ids)]
        if self.bank_id:
            dom += [('loan_agreement_id.bank_id.bank', '=',
                     self.bank_id.id)]
        if self.bank_branch_id:
            dom += [('loan_agreement_id.bank_id.bank_branch', '=',
                     self.bank_branch_id.id)]
        data['ids'] = self.env['payment.history.view'].search(dom).ids
        date_report = datetime.strptime(self.date_report, '%Y-%m-%d')
        data['parameters']['date_report'] = date_report.strftime('%d/%m/%Y')
        user = self.env.user.with_context(lang="th_TH").display_name
        data['parameters']['user'] = user
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


class PaymentHistoryView(models.Model):
    _name = 'payment.history.view'
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
    invoice_plan_id = fields.Many2one(
        'sale.invoice.plan',
        string='Invoice Plan',
        readonly=True,
    )
    payment_id = fields.Many2one(
        'account.voucher',
        string='Payment',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY lca.id, sip.id, av.id) AS id,
                   lca.id AS loan_agreement_id,
                   sip.id AS invoice_plan_id,
                   av.id AS payment_id
            FROM account_voucher av
            LEFT JOIN account_voucher_line av_line ON
                av.id = av_line.voucher_id
            LEFT JOIN account_move_line am_line ON
                av_line.move_line_id = am_line.id
            LEFT JOIN account_invoice inv ON am_line.move_id = inv.move_id
            LEFT JOIN loan_customer_agreement lca ON
                inv.loan_agreement_id = lca.id
            LEFT JOIN sale_order so ON lca.sale_id = so.id
            LEFT JOIN sale_invoice_plan sip ON
                so.id = sip.order_id AND inv.id = sip.ref_invoice_id
            WHERE av.type = 'receipt' AND av.state = 'posted' AND
                inv.loan_agreement_id IS NOT NULL
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
