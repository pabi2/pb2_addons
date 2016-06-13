# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    is_advance_clearing = fields.Boolean(
        string='Advance Clearing?',
    )

    @api.model
    def _get_invoice_total(self, invoice):
        amount_total = super(AccountInvoice, self)._get_invoice_total(invoice)
        return amount_total - self._prev_advance_amount(invoice)

    @api.model
    def _prev_advance_amount(self, invoice):
        advance_product = self.env.ref('hr_expense_advance_clearing.'
                                       'product_product_employee_advance')
        lines = invoice.invoice_line
        # Advance with Negative Amount
        advance_lines = lines.filtered(lambda x: x.price_subtotal < 0 and
                                       x.product_id == advance_product)
        return sum([l.price_subtotal for l in advance_lines])

    @api.multi
    def invoice_validate(self):
        result = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            if invoice.is_advance_clearing and not invoice.amount_total:
                move_lines = \
                    self.env['account.move.line'].search(
                        [('state', '=', 'valid'),
                         ('account_id.type', '=', 'payable'),
                         ('reconcile_id', '=', False),
                         ('move_id', '=', invoice.move_id.id),
                         ('debit', '=', 0.0), ('credit', '=', 0.0)])
                move_lines.reconcile(type='manual')
        return result
