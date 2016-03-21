# -*- coding: utf-8 -*-
from datetime import date
from openerp.tests import common


class TestAccountVoucherDeduction(common.TransactionCase):
    """
    Case:
    - Create draft invoice and validate
    - Create Voucher
    -Add multiple reconcile lines
    -Once voucher posted invoice should be paid automatically
    """
    def setUp(self):
        super(TestAccountVoucherDeduction, self).setUp()

        self.AccountInvoice = self.env['account.invoice']
        self.AccountVoucher = self.env['account.voucher']
        self.AccountVoucherMultipleReconcile = \
            self.env['account.voucher.multiple.reconcile']

        self.partner = self.env.ref("base.res_partner_3")
        self.account = self.env.ref("account.a_recv")
        self.account_bank = self.env.ref('account.bnk')
        self.product = self.env.ref("product.product_product_8")
        self.period = self.env.ref("account.period_3")
        self.sales_journal = self.env.ref("account.sales_journal")
        self.bank_journal = self.env.ref("account.bank_journal")
        self.company = self.env.ref("base.main_company")

    def test_voucher_deduction(self):
        invoice_line_val = {
            'name': 'iMac',
            'product_id': self.product.id,
            'quantity': 5,
            'price_unit': 1000.00,
        }

        self.invoice_id = self.AccountInvoice.create({
            'partner_id': self.partner.id,
            'account_id': self.account.id,
            'journal_id': self.sales_journal.id,
            'company_id': self.company.id,
            'invoice_line': [(0, 0, invoice_line_val)],
        })
        self.invoice_id.signal_workflow('invoice_open')

        self.voucher = self.AccountVoucher.create({
            'name': 'Test Voucher',
            'partner_id': self.partner.id,
            'company_id': self.company.id,
            'journal_id': self.bank_journal.id,
            'line_ids': False,
            'line_cr_ids': False,
            'account_id': self.bank_journal.default_debit_account_id.id,
            'period_id': self.period.id,
            'date': date.today(),
            'type': 'receipt',
            'amount': 3000.0,
        })
        val = self.voucher.onchange_partner_id(
            self.partner.id,
            self.voucher.journal_id.id,
            self.voucher.amount,
            self.voucher.currency_id.id,
            self.voucher.type,
            self.voucher.date
            )
        voucher_lines = [(0, 0, line) for line in val['value']['line_cr_ids']]
        self.voucher.write({'line_cr_ids': voucher_lines})

        for line in self.voucher.line_cr_ids:
            line.reconcile = True
            new_amount = line.onchange_reconcile(line.reconcile,
                                                 line.amount,
                                                 line.amount_unreconciled)
            line.write({'amount': new_amount['value']['amount']})

        self.voucher.button_reset_amount()

        self.reconcile_lines = self.AccountVoucherMultipleReconcile.create({
            'account_id': self.account_bank.id,
            'amount': self.voucher.writeoff_amount,
            'comment': 'Test voucher deduction lines',
            'voucher_id': self.voucher.id,
        })

        self.voucher.signal_workflow('proforma_voucher')
        self.assertEqual(self.voucher.state, 'posted', 'Voucher not posted.')
        self.assertEqual(self.invoice_id.state, 'paid', 'Invoice not paid.')
