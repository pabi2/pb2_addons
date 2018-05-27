# -*- coding: utf-8 -*-
# © 2016 Kitti U.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResDoctype(models.Model):
    _inherit = 'res.doctype'

    #   * Purchase Requisition
    #   * Work Acceptance
    #   * Approval Report
    #   * Stock Request
    #   * Stock Transfer
    #   * Stock Borrow
    #   * Payment Export
    #   * Bank Receipt
    #   * Interface Account
    #   * Advance Dunning Letter
    #   * Asset Change Owner
    #   * Asset Adjust
    #   * Asset Removal
    #   * Asset Request
    #   * Asset Transfer
    #   * Loan Installment
    #   * Bank Statement Reconcile
    #   * Purchase Billing
    #   * POS Order

    refer_type = fields.Selection(
        selection_add=[
            ('purchase_requisition', 'Purchase Requisition'),
            ('work_acceptance', 'Work Acceptance'),
            ('approval_report', 'Approval Report'),
            ('stock_request', 'Stock Request'),
            ('stock_transfer', 'Stock Transfer'),
            ('stock_borrow', 'Stock Borrow'),
            ('payment_export', 'Payment Export'),
            ('bank_receipt', 'Bank Receipt'),
            ('interface_account', 'Interface Account'),
            ('advance_dunning_letter', 'Advance Dunning Letter'),
            ('asset_transfer', 'Asset Transfer'),
            ('asset_changeowner', 'Asset Change Owner'),
            ('asset_request', 'Asset Request'),
            ('asset_removal', 'Asset Removal'),
            ('asset_adjust', 'Asset Adjustment'),
            ('loan_installment', 'Loan Installment'),
            ('bank_reconcile', 'Bank Statement Reconcile'),
            ('purchase_billing', 'Purchase Billing'),
            ('pos_order', 'POS Order'),
        ],
    )
