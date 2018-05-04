# -*- coding: utf-8 -*-
from openerp import api, models, fields


class LoanCreateBankInvoiceWizard(models.TransientModel):
    _name = "loan.create.bank.invoice.wizard"

    date_invoice = fields.Date(
        string='Invoice Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    amount = fields.Float(
        string='Amount',
        readonly=True,
    )

    @api.model
    def default_get(self, field_list):
        res = super(LoanCreateBankInvoiceWizard, self).default_get(field_list)
        Loan = self.env['loan.customer.agreement']
        loan = Loan.browse(self._context.get('active_id'))
        res['amount'] = loan.amount_receivable
        return res

    @api.multi
    def action_create_bank_invoice(self):
        self.ensure_one()
        Loan = self.env['loan.customer.agreement']
        loan = Loan.browse(self._context.get('active_id', False))
        loan.create_bank_invoice(self.date_invoice)
