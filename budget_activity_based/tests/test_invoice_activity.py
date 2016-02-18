# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp.tests import common
# from openerp.addons.budget_activity_based.tests import \
#     test_budget_activity_based as test_activity


class TestInvoiceActivity(common.TransactionCase):

    def setUp(self):
        super(TestInvoiceActivity, self).setUp()
        # Prepare Test Data
        self.account_payable = self.env.ref('account.a_pay')
        self.partner1 = self.env.ref('base.res_partner_1')
        self.product1 = self.env.ref('product.product_product_7')
        self.product2 = self.env.ref('product.product_product_9')
        self.activity_group_travel = \
            self.env.ref('budget_activity_based.data_activity_group_travel')
        self.activity_taxi = \
            self.env.ref('budget_activity_based.data_activity_taxi')
        self.activity_plane = \
            self.env.ref('budget_activity_based.data_activity_plane')

    def _create_invoice(self):
        line_products = [(self.product1, 1000),
                         (self.product2, 500), ]
        self.invoice_model = self.env['account.invoice']
        self.acc_type_model = self.env['account.account.type']
        self.journal_model = self.env['account.journal']
        self.product_model = self.env['product.product']
        self.inv_line_model = self.env['account.invoice.line']
        lines = []
        for product, qty in line_products:
            line_values = {
                'name': product.name,
                # 'product_id': product.id,
                'quantity': qty,
                'price_unit': 50,
                'account_id': self.account_payable.id,
            }
            lines.append((0, 0, line_values))
        inv_vals = {
            'partner_id': self.partner1.id,
            'account_id': self.partner1.property_account_payable.id,
            'name': "Test Supplier Invoice",
            'reference_type': "none",
            'type': 'in_invoice',
            'invoice_line': lines,
        }
        # Create invoice
        self.invoice =\
            self.invoice_model.sudo().create(inv_vals)

    def test_create_invoice_validate(self):
        """ Create & Validate the invoice
        1. No Activity / Product, Analytic should not be created
        2. With Activity / Product, Move Line and Analytic Line is
           created with correct chartfield
        """
        # Create Invoice
        self._create_invoice()
        # Validate the invoice
        self.invoice.sudo().signal_workflow('invoice_open')

        # 1) No Activity, Analytic should not be created
        # Check analytic account created
        account_analytic_ids = all(line.account_analytic_id for
                                   line in self.invoice.invoice_line)
        # Assert if journal entries of the invoice
        # have different operating units
        self.assertEqual(account_analytic_ids, False,
                         'Analytic created when it should not.')

        # 2) With Activity, Move Line and Analytic Line is
        #    created with correct chartfield
        self.invoice2 = self.invoice.copy()
        # line1
        self.invoice2.invoice_line[0].write(
            {'activity_group_id': self.activity_group_travel.id,
             'activity_id': self.activity_taxi.id})
        self.invoice2.invoice_line[1].write(
            {'product_id': self.product2.id})
        # Validate the invoice
        self.invoice2.sudo().signal_workflow('invoice_open')
        # Check analytic account created
        account_analytic_ids = all(line.account_analytic_id for
                                   line in self.invoice2.invoice_line)
        self.assertNotEqual(account_analytic_ids, False,
                            'Analytic is not created.')
