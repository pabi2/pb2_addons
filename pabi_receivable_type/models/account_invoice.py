# -*- coding: utf-8 -*-

from openerp import models, api, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    receivable_type = fields.Selection(
        [('advance_return', 'Advance Return'),
         ('late_work_acceptance', 'Late Work Acceptance'),
         ('loan_late_repayment', 'Late Repayment CD'),
         ('supplier_retention', 'Supplier Retention'),
         ],
        string='Receivable Type',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.onchange('receivable_type')
    def _onchange_receivable_type(self):
        self.advance_expense_id = False
        self.late_delivery_work_acceptance_id = False
        self.loan_late_payment_invoice_id = False
        self.retention_purchase_id = False
