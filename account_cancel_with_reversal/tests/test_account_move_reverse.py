# -*- coding: utf-8 -*-
from datetime import date
from openerp.tests import common


class TestAccountInvoiceCancel(common.TransactionCase):
    """
    Case1 - test_invoice_cancel:
    - Create draft invoice and validate and Cancel
    - When invoice cancel reverse entry should be generated.
    Case2 - test_voucher_cancel:
    - Create draft voucher and validate and Unreconcile
    - When voucher Unreconcile reverse entry should be generated.
    """
    def setUp(self):
        super(TestAccountInvoiceCancel, self).setUp()
        cr, uid = self.cr, self.uid
        self.account_invoice_model = self.registry('account.invoice')
        self.account_invoice_line_model = self.registry('account.invoice.line')
        self.wizard_voucher_move_reverse = \
            self.registry('account.move.reverse')
        self.account_voucher_model = self.registry('account.voucher')
        self.model_data = self.registry("ir.model.data")

        self.partner_id = self.model_data.get_object_reference(
            cr, uid, "base", "res_partner_2")[1]
        self.account_id = self.model_data.get_object_reference(
            cr, uid, "account", "a_recv")[1]
        self.product_id = self.model_data.get_object_reference(
            cr, uid, "product", "product_product_6")[1]
        self.period_id = self.model_data.get_object_reference(
            cr, uid, "account", "period_10")[1]
        self.journal_id = self.model_data.get_object_reference(
            cr, uid, "account", "bank_journal")[1]
        self.currency_id = self.model_data.get_object_reference(
            cr, uid, "base", "EUR")[1]
        self.company_id = self.model_data.get_object_reference(
            cr, uid, "base", "main_company")[1]

    def test_invoice_cancel(self):
        cr, uid = self.cr, self.uid

        invoice_line_val = {
            'name': 'LCD Screen',
            'product_id': self.product_id,
            'quantity': 5,
            'price_unit': 200,
        }

        self.invoice_id = self.account_invoice_model.create(
            cr, uid, {'partner_id': self.partner_id,
                      'account_id': self.account_id,
                      'journal_id': self.journal_id,
                      'company_id': self.company_id,
                      'invoice_line': [(0, 0, invoice_line_val)]})
        invoice = self.account_invoice_model.browse(cr, uid, self.invoice_id)
        self.account_invoice_model.signal_workflow(
            cr, uid, [self.invoice_id], 'invoice_open')
        self.assertEqual(invoice.state, 'open', 'Invoice not validated.')
        move_id = invoice.move_id

        reverse_move_id = move_id.create_reversals(
            date.today(),
            reversal_period_id=self.period_id,
            reversal_journal_id=self.journal_id,
            move_prefix='REV-',
            move_line_prefix='REV-',
            )
        reverse_move = self.registry('account.move').\
            browse(cr, uid, reverse_move_id[0])
        self.assertNotEqual(reverse_move.state, 'posted', 'Move posted.')
        self.account_invoice_model.write(
            cr, uid, [self.invoice_id], {'cancel_move_id': reverse_move_id[0]})

        self.assertTrue(invoice.cancel_move_id, 'Reverse move not created.')

        # reconcile new journal entry
        self.account_invoice_model.signal_workflow(
            cr, uid, [self.invoice_id], 'invoice_cancel')
        self.wizard_voucher_move_reverse.reconcile_reverse_journals(
            cr, uid, [reverse_move_id[0], move_id.id])

        self.assertEqual(invoice.state, 'cancel', 'Invoice not cancelled')

    def test_voucher_cancel(self):
        cr, uid = self.cr, self.uid
        self.voucher_id = self.account_voucher_model.create(cr, uid, {
            'name': 'Test Voucher',
            'partner_id': self.partner_id,
            'company_id': self.company_id,
            'journal_id': self.journal_id,
            'line_ids': False,
            'line_cr_ids': False,
            'account_id': self.account_id,
            'period_id': self.period_id,
            'date': date.today(),
            'type': 'receipt',
            'amount': 110.0,
        })
        self.voucher = self.account_voucher_model.browse(
            cr, uid, self.voucher_id)

        val = self.account_voucher_model.onchange_partner_id(
            cr, uid, [self.voucher_id],
            self.partner_id,
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
        move_id = self.voucher.move_id
        reverse_move_id = move_id.create_reversals(
            self.voucher.date,
            reversal_period_id=self.period_id,
            reversal_journal_id=self.journal_id,
            move_prefix='REV-',
            move_line_prefix='REV-',
            )
        self.voucher.write({'cancel_move_id': reverse_move_id[0]})
        self.assertTrue(self.voucher.cancel_move_id,
                        'Reverse move not created.')
        self.voucher.cancel_voucher()
        self.wizard_voucher_move_reverse.reconcile_reverse_journals(
            cr, uid, [reverse_move_id[0], move_id.id])
        self.assertEqual(self.voucher.state, 'cancel', 'Voucher not cancelled')
