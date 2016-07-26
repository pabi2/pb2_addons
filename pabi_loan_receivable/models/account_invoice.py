# -*- coding: utf-8 -*-
from datetime import datetime
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    loan_agreement_id = fields.Many2one(
        'loan.customer.agreement',
        string='Loan Agreement',
        readonly=True,
        copy=False,
    )
    loan_late_payment_invoice_id = fields.Many2one(
        'account.invoice',
        string="CD Loan Late Payment",
        help="List CD Loan customer invoice which is paid after its due date "
        "which has not been paying for its penalty"
    )

    @api.multi
    def onchange_partner_id(self, ttype, partner_id, date_invoice=False,
                            payment_term=False, partner_bank_id=False,
                            company_id=False):
        res = super(AccountInvoice, self).onchange_partner_id(
            ttype, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id)
        if not res:
            res = {}
        if 'value' not in res:
            res['value'] = {}
        if 'domain' not in res:
            res['domain'] = {}

        res['value'].update({'loan_late_payment_invoice_id': False})
        if not partner_id:
            domain = [('id', 'in', [])]
            res['domain'].update({'loan_late_payment_invoice_id': domain})
        else:
            self._cr.execute("""
                select ai.id from account_invoice ai
                join loan_customer_agreement lca on
                    lca.id = ai.loan_agreement_id
                where ai.partner_id = %s
                and ai.date_paid > (ai.date_due + lca.days_grace_period)
                and ai.state = 'paid'
                and ai.id not in (select distinct loan_late_payment_invoice_id
                                from account_invoice where partner_id = %s
                                and loan_late_payment_invoice_id is not null
                                and state in ('open', 'paid'))
                order by ai.id
            """, (partner_id, partner_id,))
            invoice_ids = [x[0] for x in self._cr.fetchall()]
            domain = [('id', 'in', invoice_ids)]
            res['domain'].update({'loan_late_payment_invoice_id': domain})
        return res

    @api.onchange('loan_late_payment_invoice_id')
    def _onchange_loan_late_payment_invoice_id(self):
        # This method is called from Customer invoice to charge penalty
        if self.loan_late_payment_invoice_id:
            self.invoice_line = []
            late_invoice = self.loan_late_payment_invoice_id
            penalty_line = self.env['account.invoice.line'].new()
            loan = self.loan_late_payment_invoice_id.loan_agreement_id
            penalty_rate = loan.fy_penalty_rate / 365
            date_paid = datetime.strptime(late_invoice.date_paid, '%Y-%m-%d')
            date_due = datetime.strptime(late_invoice.date_due, '%Y-%m-%d')
            days = (date_paid - date_due).days
            amount_penalty = days * penalty_rate * late_invoice.amount_total
            # Prepare header
            self.currency_id = late_invoice.currency_id
            # Prepare line
            product = self.env['ir.property'].get(
                'property_loan_penalty_product_id', 'res.partner')
            if not product:
                raise ValidationError(_('No Loan Penalty Product has been '
                                        'set in Account Settings!'))
            penalty_line.product_id = product
            penalty_line.name = _('%s (%s Days)') % (product.name, days)
            penalty_line.quantity = 1.0
            penalty_line.price_unit = amount_penalty
            self.invoice_line += penalty_line
