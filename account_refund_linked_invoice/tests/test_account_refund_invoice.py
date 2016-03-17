# -*- coding: utf-8 -*-
from datetime import date
from openerp.tests import common


class TestAccountRefundLinkedInvoice(common.TransactionCase):
    """
    Case:
    - Create draft invoice and validate
    - Create refund invoice
    - refund invoice linked up with original invoice
    and compute total refund amount.
    """
    def setUp(self):
        super(TestAccountRefundLinkedInvoice, self).setUp()

        self.AccountInvoice = self.env['account.invoice']
        self.AccountInvoiceRefund = self.env['account.invoice.refund']

        self.partner = self.env.ref("base.res_partner_2")
        self.account = self.env.ref("account.a_recv")
        self.product = self.env.ref("product.product_product_8")
        self.period = self.env.ref("account.period_3")
        self.sales_journal = self.env.ref("account.sales_journal")
        self.company = self.env.ref("base.main_company")

        self.account_invoice_refund = self.AccountInvoiceRefund.create({
            'date': date.today(),
            'period': self.period.id,
            'description': 'Test Refund',
            'filter_refund': 'refund'
        })

    def test_invoice_refund(self):
        invoice_line_val = {
            'name': 'iMac',
            'product_id': self.product.id,
            'quantity': 5,
            'price_unit': 1799.00,
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
        ctx.update({'active_ids': [self.invoice_id.id],
                    'active_id': self.invoice_id.id})
        self.refund_invoice = self.account_invoice_refund.\
            with_context(ctx).invoice_refund()

        self.assertNotEqual(self.invoice_id.refund_invoice_ids, False,
                            'Refund not created.')
