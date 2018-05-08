# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp.tests import common
import ast
# from openerp.addons.accoun_budget_activity.tests import \
#     test_accoun_budget_activity as test_activity


class TestPrToReqToPo(common.TransactionCase):

    # Case:
    # for PR -> Call for Bid -> RFQ
    # Make sure that,
    # 1) Activity / Product is passed.
    # 2) Analytic is created if not yet done so.
    def setUp(self):
        super(TestPrToReqToPo, self).setUp()
        self.PurchaseRequest = \
            self.env['purchase.request']
        self.PurchaseRequisition = \
            self.env['purchase.requisition']
        self.PurchaseOrder = \
            self.env['purchase.order']
        self.WizardMakeRequisition = \
            self.env['purchase.request.line.make.purchase.requisition']
        self.purchase_request = \
            self.env.ref('account_budget_activity.demo_purchase_request_0')
        self.partner1 = self.env.ref('base.res_partner_1')

    def test_purchase_request(self):
        """ Approve Purchase Request
        Analytic should be created, if not yet created
        """
        self.purchase_request.button_to_approve()
        account_analytic_ids = [line.analytic_account_id
                                for line in self.purchase_request.line_ids]
        self.assertEqual(len(account_analytic_ids),
                         len(self.purchase_request.line_ids),
                         'All PR Line do not have Analytic Account')

    def _create_requisition(self):
        self.purchase_request.button_to_approve()
        self.purchase_request.button_approved()
        # Prepare wizard
        Wizard = self.WizardMakeRequisition.\
            with_context(active_model='purchase.request.line',
                         active_ids=self.purchase_request.line_ids._ids)
        res = Wizard.default_get([])
        wizard = Wizard.create(res)
        # Click create Call for Bid, its activity must equal
        res = wizard.make_purchase_requisition()
        domain = ast.literal_eval(res['domain'])
        domain = list(set(domain[0][2]))
        return self.PurchaseRequisition.search([('id', 'in', domain)])

    def test_call_for_bid(self):
        """ Create Call for Bid
        Activity should be passed correctly
        """
        requisition = self._create_requisition()
        for line in requisition.line_ids:
            self.assertEqual(
                line.activity_id,
                line.purchase_request_lines.activity_id,
                'Activity in requisition line not equal to its '
                'reference in purchase request line')

    def _create_rfq(self):
        self.requisition = self._create_requisition()
        self.requisition.sudo().signal_workflow('sent_suppliers')
        return self.requisition.make_purchase_order(self.partner1.id)

    def test_rfq(self):
        """ Create RFQ from Call for Bid
        Activity should be passed correctly
        """
        res = self._create_rfq()
        rfq_id = res[self.requisition.id]
        rfq = self.PurchaseOrder.browse(rfq_id)
        for line in rfq.order_line:
            self.assertEqual(
                line.activity_id,
                line.requisition_line_id.activity_id,
                'Activity in order line not equal to its '
                'reference in purchase requisition line')
