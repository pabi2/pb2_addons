# -*- coding: utf-8 -*-
import time
from openerp.tests import common


class TestAccountInvoiceOverwriteDueDate(common.TransactionCase):
    """
    Case:
    - Create draft invoice with payment term 15 days
    - Specify due date and validate, due date should not change
    - Do not specify due date and validate, due date should change
    """
    def setUp(self):
        super(TestAccountInvoiceOverwriteDueDate, self).setUp()
        self.invoice = self.env.ref(
            'account_invoice_overwrite_duedate.demo_invoice_no_duedate')

    def test_no_duedate_system_suggest(self):
        # Invoice Date is YYYY-01-01 and no due date
        self.invoice.signal_workflow('invoice_open')
        # Due Date should be YYYY-01-16
        self.assertEqual(self.invoice.date_due,
                         time.strftime('%Y')+'-01-16',
                         'Suggested due date is not correct '
                         'according to payment term')

    def test_with_duedate_overwrite_suggest(self):
        # Setup a due date
        self.invoice.date_due = time.strftime('%Y')+'-02-01'
        self.invoice.signal_workflow('invoice_open')
        # Due Date should be YYYY-02-01
        self.assertEqual(self.invoice.date_due,
                         time.strftime('%Y')+'-02-01',
                         'Suggested due date is not correct '
                         'according to payment term')
