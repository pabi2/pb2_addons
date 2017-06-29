# -*- coding: utf-8 -*-
from datetime import date
from openerp.tests import common


class TestHRExpenseAutoInvoice(common.TransactionCase):
    """
    Case:
    - Expense can have tax now. Total = Amount + Tax
    - Upon generate account entries (last step), invoice will be created
    - Employee / Partner and Amount in invoice must equal to expense
    - Once invoice is paid, the expense state will be paid too
    - If invoice is cancelled, the expense should back to cancelled
    - And if invoice is back to Open, expense should back to waiting payment
    """
    def setUp(self):
        super(TestHRExpenseAutoInvoice, self).setUp()
        self.account_obj = self.env['account.account']
        self.expense_obj = self.env['hr.expense.expense']
        self.product_obj = self.env['product.product']
        self.tax_obj = self.env['account.tax']
        self.code_obj = self.env['account.tax.code']
        self.voucher_model = self.env['account.voucher']
        self.product = self.env.ref('hr_expense.air_ticket')
        self.employee = self.env.ref('hr.employee_mit')
        self.partner = self.env.ref('base.res_partner_19')
        self.base_code_id = self.code_obj.create({'name': 'Expense Base Code'})
        self.tax = self.tax_obj.create({
            'name': 'Expense 10%',
            'amount': 0.10,
            'type': 'percent',
            'type_tax_use': 'purchase',
            'price_include': False,
            'base_code_id': self.base_code_id.id,
            'base_sign': -1,
        })
        # Expense
        exp_line_val = {
            'name': 'Car Travel Expenses',
            'product_id': self.product.id,
            'unit_amount': 100.00,
            'tax_ids': [(6, 0, [self.tax.id])],
        }
        exp_val = {
            'name': 'Expense for Minh Tran',
            'employee_id': self.employee.id,
            'pay_to': 'supplier',
            'partner_id': self.partner.id,
            'line_ids': [(0, 0, exp_line_val)],
        }
        self.expense = self.expense_obj.create(exp_val)
        self.account = self.account_obj.search(
            [('type', '=', 'payable'), ('currency_id', '=', False)],
            limit=1)[0]
        self.voucher = self.voucher_model.create({
            'date': str(date.today().year) + '-01-01',
            'name': "Test", 'amount': 110.0,
            'account_id': self.account.id,
            'partner_id': self.partner.id,
            'type': 'payment',
        })

    def test_auto_invoice(self):
        # Test amount + tax
        self.assertEquals(self.expense.amount, 110.0,
                          'Tax is not included in total amount')
        self.expense.signal_workflow('confirm')
        self.expense.signal_workflow('validate')
        self.expense.signal_workflow('done')
        self.assertEquals(self.expense.state, 'done',
                          'Expense is not in Waiting Payment state')
        # Create invoice
        self.assertTrue(self.expense.invoice_id,
                        'Invoice is not created')
        self.assertEqual(self.expense.invoice_id.state, 'open',
                         'Invoice is not in state "Open"')
        self.assertEqual(self.expense.invoice_id.move_id,
                         self.expense.account_move_id,
                         'Journal Entry is not the same as of invoice')
        # Amount in invoice must equal to expense
        self.assertEqual(self.expense.amount,
                         self.expense.invoice_id.amount_total,
                         'Amount in expense is not equal to amount in invoice')
        # Create Supplier Payment
        val = self.voucher.onchange_partner_id(
            self.partner.id,
            self.voucher.journal_id.id,
            self.voucher.amount,
            self.voucher.currency_id.id,
            self.voucher.type,
            self.voucher.date
        )
        voucher_lines = [(0, 0, line) for line in val['value']['line_dr_ids']]
        self.voucher.write({'line_dr_ids': voucher_lines})
        # Paid
        self.voucher.signal_workflow('proforma_voucher')
        self.assertEqual(self.expense.state,
                         'paid',
                         'Paid but expense is not marked as paid')

    def test_auto_invoice_cancel(self):
        self.expense.signal_workflow('confirm')
        self.expense.signal_workflow('validate')
        self.expense.signal_workflow('done')
        # Cancel Invoice, make sure it can be cancelled
        self.invoice = self.expense.invoice_id
        self.invoice.journal_id.update_posted = True  # allow cancel JE
        self.invoice.signal_workflow('invoice_cancel')
        self.assertEqual(self.expense.state, 'cancelled',
                         'Invoice is cancelled but expense is not cancelled')
        # Invoice is set to draft, expense stay cancelled
        self.invoice.action_cancel_draft()
        self.assertEqual(self.expense.state, 'cancelled',
                         'Invoice is draft but expense is not cancelled')
        # Invoice is set to open, expense back to waiting payment
        self.invoice.signal_workflow('invoice_open')
        self.assertEqual(self.expense.state, 'done',
                         'Invoice is open, but expense is '
                         'not back to waiting payment')
        # Create Supplier Payment
        val = self.voucher.onchange_partner_id(
            self.partner.id,
            self.voucher.journal_id.id,
            self.voucher.amount,
            self.voucher.currency_id.id,
            self.voucher.type,
            self.voucher.date
        )
        voucher_lines = [(0, 0, line) for line in val['value']['line_dr_ids']]
        self.voucher.write({'line_dr_ids': voucher_lines})
        # Paid
        self.voucher.signal_workflow('proforma_voucher')
        self.assertEqual(self.expense.state,
                         'paid',
                         'Paid but expense is not marked as paid')
