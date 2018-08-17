# -*- coding: utf-8 -*-
from openerp import models, fields, api


class XLSXReportCDReceivableBalanceSheetDetail(models.TransientModel):
    _name = 'xlsx.report.cd.receivable.balance.sheet.detail'
    _inherit = 'report.account.common'

    partner_ids = fields.Many2many(
        'res.partner',
        'cd_receivable_balance_sheet_detail_partner_rel',
        'report_id', 'partner_id',
        string='Customers',
    )
    mou_ids = fields.Many2many(
        'loan.bank.mou',
        'cd_receivable_balance_sheet_detail_mou_rel',
        'report_id', 'mou_id',
        string='MOU',
    )
    account_ids = fields.Many2many(
        'account.account',
        'cd_receivable_balance_sheet_detail_account_rel',
        'report_id', 'account_id',
        string='Accounts',
        default=lambda self: self.env['account.account'].search(
            [('code', '=', '1102010006')]),
        readonly=True,
    )
    results = fields.One2many(
        'cd.receivable.balance.sheet.detail',
        'wizard_id',
        string='Balance Sheet Detail Results',
    )

    @api.multi
    def get_dom_loan_agreement(self):
        dom = [('sale_id.state', 'not in', ('draft', 'cancel'))]
        if self.partner_ids:
            dom += [('borrower_partner_id', 'in', self.partner_ids.ids)]
        if self.mou_ids:
            dom += [('mou_id', 'in', self.mou_ids.ids)]
        if self.account_ids:
            dom += [('account_receivable_id', 'in', self.account_ids.ids)]
        return dom

    @api.multi
    def get_dom_brought_forward(self, loan_agreements):
        Fiscalyear = self.env['account.fiscalyear']
        date_start = \
            Fiscalyear.search([], order="date_start", limit=1).date_start
        if self.fiscalyear_start_id:
            date_start = self.fiscalyear_start_id.date_start
        if self.period_start_id:
            date_start = self.period_start_id.date_start
        if self.date_start:
            date_start = self.date_start
        dom = [('loan_agreement_id', 'in', loan_agreements.ids),
               ('invoice_id.state', '=', 'paid'),
               ('invoice_id.date_due', '<', date_start)]
        return dom

    @api.multi
    def get_dom_common_invoice(self, loan_agreements):
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
            date_start = self.period_start_id.date_start
        if self.period_end_id:
            date_end = self.period_end_id.date_stop
        if self.date_start:
            date_start = self.date_start
        if self.date_end:
            date_end = self.date_end
        dom = [('loan_agreement_id', 'in', loan_agreements.ids),
               ('invoice_id.state', '=', 'paid'),
               ('invoice_id.date_due', '>=', date_start),
               ('invoice_id.date_due', '<=', date_end)]
        return dom

    @api.multi
    def get_dom_supplier_payment(self, loan_agreements):
        dom = self.get_dom_common_invoice(loan_agreements)
        return dom + [('invoice_id.type', '=', 'in_invoice')]

    @api.multi
    def get_dom_customer_invoice(self, loan_agreement):
        dom = self.get_dom_common_invoice(loan_agreement)
        return dom + [('invoice_id.type', '=', 'out_invoice')]

    @api.multi
    def get_loan_agreements(self):
        LoanAgreement = self.env['loan.customer.agreement']
        dom = self.get_dom_loan_agreement()
        loan_agreements = LoanAgreement.search(dom)
        return loan_agreements

    @api.multi
    def get_brought_forwards(self, loan_agreements):
        LoanAgreementView = self.env['loan.customer.agreement.view']
        dom = self.get_dom_brought_forward(loan_agreements)
        brought_forwards = LoanAgreementView.search(dom)
        return brought_forwards

    @api.multi
    def get_supplier_payments(self, loan_agreements):
        LoanAgreementView = self.env['loan.customer.agreement.view']
        dom = self.get_dom_supplier_payment(loan_agreements)
        supplier_payments = LoanAgreementView.search(dom)
        return supplier_payments

    @api.multi
    def get_customer_invoices(self, loan_agreements):
        LoanAgreementView = self.env['loan.customer.agreement.view']
        dom = self.get_dom_customer_invoice(loan_agreements)
        customer_invoices = LoanAgreementView.search(dom)
        return customer_invoices

    @api.multi
    def get_execute_datas(self, loan_agreements, brought_forwards,
                          supplier_payments, customer_invoices):
        # Set loan agreement ids
        loan_agreement_ids = loan_agreements.ids
        if len(loan_agreement_ids) in [0, 1]:
            loan_agreement_ids.extend([0, 0])
        # Set brought forward ids
        brought_forward_ids = brought_forwards.ids
        if len(brought_forward_ids) in [0, 1]:
            brought_forward_ids.extend([0, 0])
        # Set supplier payment ids
        supplier_payment_ids = supplier_payments.ids
        if len(supplier_payment_ids) in [0, 1]:
            supplier_payment_ids.extend([0, 0])
        # Set customer invoice ids
        customer_invoice_ids = customer_invoices.ids
        if len(customer_invoice_ids) in [0, 1]:
            customer_invoice_ids.extend([0, 0])
        self._cr.execute("""
            SELECT lca.id AS loan_agreement_id, bf.brought_forward,
                   sp.voucher_id AS supplier_payment_id, ci.invoice_plan_id
            FROM loan_customer_agreement lca
            LEFT JOIN (SELECT lcav.loan_agreement_id,
                              SUM(CASE WHEN inv.type = 'in_invoice' THEN
                                  inv.amount_total ELSE (-1) * inv.amount_total
                                  END) AS brought_forward
                       FROM loan_customer_agreement_view lcav
                       LEFT JOIN account_invoice inv ON
                        lcav.invoice_id = inv.id
                       WHERE lcav.id IN %s
                       GROUP BY lcav.loan_agreement_id) bf
                ON lca.id = bf.loan_agreement_id
            LEFT JOIN (SELECT lcav.loan_agreement_id, avl.voucher_id
                       FROM loan_customer_agreement_view lcav
                       LEFT JOIN account_voucher_line avl
                        ON lcav.invoice_id = avl.invoice_id
                       LEFT JOIN account_voucher av ON avl.voucher_id = av.id
                       WHERE lcav.id IN %s AND av.state = 'posted') sp
                ON lca.id = sp.loan_agreement_id
            LEFT JOIN (SELECT lcav.loan_agreement_id, sip.id AS invoice_plan_id
                       FROM loan_customer_agreement_view lcav
                       LEFT JOIN sale_invoice_plan sip
                        ON lcav.invoice_id = sip.ref_invoice_id
                       WHERE lcav.id IN %s) ci ON lca.id = ci.loan_agreement_id
            WHERE lca.id IN %s
            ORDER BY lca.borrower_partner_id, lca.mou_id, lca.sale_id, lca.name
        """ % (str(tuple(map(int, brought_forward_ids))),
               str(tuple(map(int, supplier_payment_ids))),
               str(tuple(map(int, customer_invoice_ids))),
               str(tuple(loan_agreement_ids))))
        return self._cr.fetchall()

    @api.multi
    def prepare_cd_receivable_balance_sheet_details(self, datas):
        LoanAgreement = self.env['loan.customer.agreement']
        Voucher = self.env['account.voucher']
        InvoicePlan = self.env['sale.invoice.plan']
        lines = []
        total_invoice_amount = 0
        for loan_agreement_id in list(set(map(lambda x: x[0], datas))):
            loan_agreement = LoanAgreement.browse(loan_agreement_id)
            first_rec = True
            subtotal_invoice_amount = 0
            old_outstanding = 0
            for rec in filter(lambda x: x[0] == loan_agreement_id, datas):
                supplier_payment = Voucher.browse(rec[2] or 0)
                invoice_plan = InvoicePlan.browse(rec[3] or 0)
                lines.append((0, 0, {
                    'partner_code':
                        first_rec and loan_agreement.borrower_partner_id
                        .search_key or False,
                    'partner_name': first_rec and " ".join(
                        list(filter(lambda l: l is not False,
                                    [loan_agreement.borrower_partner_id
                                        .title.name,
                                     loan_agreement.borrower_partner_id
                                        .name])))
                        or False,
                    'mou': first_rec and loan_agreement.mou_id.name or False,
                    'brought_forward': first_rec and rec[1] or False,
                    'supplier_payment_number':
                        first_rec and supplier_payment.number or False,
                    'supplier_payment_posting_date':
                        first_rec and supplier_payment.date or False,
                    'supplier_payment_amount':
                        first_rec and supplier_payment.amount or False,
                    'installment': invoice_plan.installment,
                    'customer_invoice_number':
                        invoice_plan.ref_invoice_id.number,
                    'customer_invoice_posting_date':
                        invoice_plan.ref_invoice_id.date_invoice,
                    'customer_invoice_amount':
                        invoice_plan.ref_invoice_id.amount_total,
                    'outstanding': first_rec and
                        ((rec[1] and rec[1] or 0) + supplier_payment.amount -
                         invoice_plan.ref_invoice_id.amount_total) or
                        not first_rec and
                        (old_outstanding -
                         invoice_plan.ref_invoice_id.amount_total) or False,
                }))
                first_rec = False
                old_outstanding = (rec[1] and rec[1] or 0) + \
                    supplier_payment.amount - \
                    invoice_plan.ref_invoice_id.amount_total
                subtotal_invoice_amount += \
                    invoice_plan.ref_invoice_id.amount_total
            total_invoice_amount += subtotal_invoice_amount
            # Subtotal
            lines.append((0, 0, {
                'partner_code': 'Subtotal',
                'customer_invoice_amount': subtotal_invoice_amount,
            }))
        # Grand Total
        lines.append((0, 0, {
            'partner_code': 'Grand Total',
            'customer_invoice_amount': total_invoice_amount,
        }))
        return lines

    @api.multi
    def create_cd_receivable_balance_sheet_detail(self):
        # Get loan agreements
        loan_agreements = self.get_loan_agreements()

        # Get brought forwards
        brought_forwards = self.get_brought_forwards(loan_agreements)

        # Get supplier payments
        supplier_payments = self.get_supplier_payments(loan_agreements)

        # Get customer invoices
        customer_invoices = self.get_customer_invoices(loan_agreements)

        # Get execute datas
        datas = self.get_execute_datas(
            loan_agreements, brought_forwards, supplier_payments,
            customer_invoices)

        # Prepare cd receivable balance sheet details
        lines = self.prepare_cd_receivable_balance_sheet_details(datas)

        # Write data
        self.write({'results': lines})
        return True

    @api.multi
    def action_get_report(self):
        self.create_cd_receivable_balance_sheet_detail()
        res = super(XLSXReportCDReceivableBalanceSheetDetail, self) \
            .action_get_report()
        return res


class CDReceivableBalanceSheetDetail(models.TransientModel):
    _name = 'cd.receivable.balance.sheet.detail'
    _order = 'id'

    partner_code = fields.Char(
        string='Partner Code',
    )
    partner_name = fields.Char(
        string='Partner Name',
    )
    mou = fields.Char(
        string='MOU',
    )
    brought_forward = fields.Float(
        string='Brought Forward',
    )
    supplier_payment_number = fields.Char(
        string='Supplier Payment Number',
    )
    supplier_payment_posting_date = fields.Date(
        string='Supplier Payment Posting Date',
    )
    supplier_payment_amount = fields.Float(
        string='Supplier Payment Amount',
    )
    installment = fields.Integer(
        string='Installment',
    )
    customer_invoice_number = fields.Char(
        string='Customer Invoice Number',
    )
    customer_invoice_posting_date = fields.Date(
        string='Customer Invoice Posting Date',
    )
    customer_invoice_amount = fields.Float(
        string='Customer Invoice Amount',
    )
    outstanding = fields.Float(
        string='Outstanding',
    )
    wizard_id = fields.Many2one(
        'xlsx.report.cd.receivable.balance.sheet.detail',
        string='CD Receivable Balance Sheet Detail Wizard',
    )
