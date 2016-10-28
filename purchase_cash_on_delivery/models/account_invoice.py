# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_prepaid = fields.Boolean(
        string='Cash on Delivery',
        compute='_compute_is_prepaid',
        store=True,
    )
    clear_prepaid_move_id = fields.Many2one(
        'account.move',
        string='Clear Prepaid Journal Entry',
        readonly=True,
        index=True,
        ondelete='restrict',
        copy=False,
    )

    @api.multi
    @api.depends('payment_term')
    def _compute_is_prepaid(self):
        cod_pay_term = self.env.ref('purchase_cash_on_delivery.'
                                    'cash_on_delivery_payment_term')
        for rec in self:
            if rec.payment_term == cod_pay_term:
                rec.is_prepaid = True
            else:
                rec.is_prepaid = False


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
                    _('No prepaid account has been set for case '
                      'Cash on Delivery!'))
        return res
