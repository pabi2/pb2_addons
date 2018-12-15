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
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="List CD Loan customer invoice which is paid after its due date "
        "which has not been paying for its penalty"
    )
    discard_installment_order_check = fields.Boolean(
        string='Discard Installment Order Check',
        help="If checked, user can validate this loan "
        "invoice regardless of the installment order. "
        "This flag is only valid in Loan Agreement context.",
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
        res['value'].update({'loan_late_payment_invoice_id': False})
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        partner_id = self._context.get('loan_late_payment_customer_id', False)
        if 'loan_late_payment_customer_id' in self._context and not partner_id:
            args += [('id', 'in', [])]
        if partner_id:
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
            args += domain
        return super(AccountInvoice, self).name_search(name=name,
                                                       args=args,
                                                       operator=operator,
                                                       limit=limit)

    @api.model
    def _get_account_id_from_product(self, product, fpos):
        account_id = product.property_account_expense.id
        if not account_id:
            categ = product.categ_id
            account_id = categ.property_account_expense_categ.id
        if not account_id:
            raise ValidationError(
                _('Define an expense account for this '
                  'product: "%s" (id:%d).') %
                (product.name, product.id,))
        if fpos:
            account_id = fpos.map_account(account_id)
        return account_id

    @api.onchange('loan_late_payment_invoice_id')
    def _onchange_loan_late_payment_invoice_id(self):
        # This method is called from Customer invoice to charge penalty
        if self.loan_late_payment_invoice_id:
            self.invoice_line = False
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
            product = self.env.user.company_id.loan_penalty_product_id
            if not product:
                raise ValidationError(_('No Loan Penalty Product has been '
                                        'set in Account Settings!'))
            penalty_line.product_id = product
            penalty_line.account_id = self.\
                _get_account_id_from_product(product, self.fiscal_position)
            penalty_line.name = (u'%s (%s วัน) เอกสารเลขที่ %s' %
                                 (product.name, days, late_invoice.number))
            penalty_line.quantity = 1.0
            penalty_line.price_unit = amount_penalty
            self.invoice_line += penalty_line

    @api.model
    def _check_loan_invoice_in_advance(self, loan_agreement_id, date_due):
        if loan_agreement_id:
            dom = [('type', 'in', ('out_invoice', 'out_refund')),
                   ('state', '=', 'draft'),
                   ('date_due', '<', date_due),
                   ('loan_agreement_id', '=', loan_agreement_id), ]
            if self.search_count(dom) > 0:
                raise ValidationError(
                    _('You are not allowed to validate '
                      'invoice plan in advance!'))
        return

    @api.multi
    def action_move_create(self):
        result = super(AccountInvoice, self).action_move_create()
        # For loan case, not allow validate invoice plan in advance
        for invoice in self:
            if invoice.discard_installment_order_check:
                continue
            self._check_loan_invoice_in_advance(invoice.loan_agreement_id.id,
                                                invoice.date_due)
        return result


# class AccountInvoiceLine(models.Model):
#     _inherit = 'account.invoice.line'
#
#     @api.model
#     def create(self, vals):
#         return super(AccountInvoiceLine, self).create(vals)
