# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_prepaid = fields.Boolean(
        string='Cash on Delivery',
        compute='_compute_is_prepaid',
        store=True,
    )

    @api.multi
    @api.depends('payment_term_id')
    def _compute_is_prepaid(self):
        cod_pay_term = self.env.ref('purchase_cash_on_delivery.'
                                    'cash_on_delivery_payment_term', False)
        for rec in self:
            rec.is_prepaid = rec.payment_term_id == cod_pay_term

    @api.onchange('payment_term_id', 'invoice_method')
    def _onchange_cash_on_delivery(self):
        cod_pay_term = self.env.ref('purchase_cash_on_delivery.'
                                    'cash_on_delivery_payment_term')
        if self.payment_term_id.id == cod_pay_term.id:
            self.invoice_method = 'order'

    @api.multi
    @api.constrains('payment_term_id', 'invoice_method')
    def _check_cash_on_delivery(self):
        cod_pay_term = self.env.ref('purchase_cash_on_delivery.'
                                    'cash_on_delivery_payment_term')
        for purchase in self:
            if purchase.payment_term_id.id == cod_pay_term.id and \
                    purchase.invoice_method != 'order':
                raise ValidationError(
                    _('For payment term "Cash on Delivery", Invoice Control '
                      'must be "Based on generated draft invoice" !'))

    @api.multi
    def _validate_purchase_cod_fully_paid(self):
        cod_pay_term = self.env.ref('purchase_cash_on_delivery.'
                                    'cash_on_delivery_payment_term')
        # If not fully paid
        for purchase in self:
            if purchase.invoice_method == 'order' and \
                    purchase.payment_term_id.id == cod_pay_term.id:
                if not purchase.invoiced or \
                    False in [x.state == 'paid' and True or False
                              for x in purchase.invoice_ids]:
                    raise ValidationError(
                        _('For cash on delivery (COD), tranfer is allowed '
                          'only when all invoice(s) are fully paid!'))
        return True

    @api.multi
    def view_picking(self):
        self._validate_purchase_cod_fully_paid()
        return super(PurchaseOrder, self).view_picking()
