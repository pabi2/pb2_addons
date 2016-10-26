# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def move_line_get_item(self, line):
        res = super(AccountInvoiceLine, self).move_line_get_item(line)
        cod_pay_term = self.env.ref('purchase_cash_on_delivery.'
                                    'cash_on_delivery_payment_term')
        if line.invoice_id.payment_term == cod_pay_term:
            prepaid_account_id = self.env.user.company_id.prepaid_account_id.id
            if prepaid_account_id:
                res.update({'account_id': prepaid_account_id})
            else:
                raise ValidationError(
                    _('No prepaid account has bee set for case '
                      'Cash on Delivery!'))
        return res
