# -*- coding: utf-8 -*-
from datetime import date
from openerp.tests import common


class TestAccountCancelWithReversal(common.TransactionCase):
    """
    Case1 - test_invoice_cancel:
    - Create draft invoice and validate and Cancel
    - When invoice cancel reverse entry should be generated.
    Case2 - test_voucher_cancel:
    - Create draft voucher and validate and Unreconcile
    - When voucher Unreconcile reverse entry should be generated.
    """
    def setUp(self):
        super(TestAccountCancelWithReversal, self).setUp()

        self.AccountInvoice = self.env['account.invoice']
        self.AccountMoveReverse = self.env['account.move.reverse']
        self.AccountVoucher = self.env['account.voucher']

        self.partner = self.env.ref("base.res_partner_2")
        self.account = self.env.ref("account.a_recv")
        self.product = self.env.ref("product.product_product_6")
        self.period = self.env.ref("account.period_10")
        self.bank_journal = self.env.ref("account.bank_journal")
        self.sales_journal = self.env.ref("account.sales_journal")
        self.company = self.env.ref("base.main_company")

        self.account_move_reverse_wizard = self.AccountMoveReverse.create({
            'date': date.today(),
            'period_id': self.period.id,
            'journal_id': self.bank_journal.id,
            'move_prefix': 'REV-',
            'move_line_prefix': 'REV-',
        })

    def test_invoice_cancel(self):
        invoice_line_val = {
            'name': 'LCD Screen',
            'product_id': self.product.id,
            'quantity': 5,
            'price_unit': 200,
        }

        self.invoice_id = self.AccountInvoice.create({
            'partner_id': self.partner.id,
            'account_id': self.account.id,
            'journal_id': self.sales_journal.id,
            'company_id': self.company.id,
            'invoice_line': [(0, 0, invoice_line_val)],
        })
        self.invoice_id.signal_workflow('invoice_open')
        self.assertEqual(self.invoice_id.state, 'open',
                         'Invoice not validated.')
        ctx = self.env.context.copy()
        ctx.update({'active_ids': [self.invoice_id.id]})
        self.account_move_reverse_wizard.with_context(ctx).\
            action_reverse_invoice()
        self.assertEqual(self.invoice_id.state, 'cancel',
                         'Invoice not cancelled')

    def test_voucher_cancel(self):
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
            'amount': 110.0,
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
        # Paid
        self.voucher.signal_workflow('proforma_voucher')
        self.assertEqual(self.voucher.state, 'posted', 'Voucher not posted.')
        ctx = self.env.context.copy()
        ctx.update({'active_ids': [self.voucher.id]})
        self.account_move_reverse_wizard.with_context(ctx).\
            action_reverse_voucher()

        self.assertEqual(self.voucher.state, 'cancel', 'Voucher not cancelled')
