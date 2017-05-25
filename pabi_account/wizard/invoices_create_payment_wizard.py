# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class InovicesCreatePaymentWizard(models.TransientModel):
    _inherit = 'invoices.create.payment.wizard'

    @api.multi
    def _validate(self, invoices):
        res = super(InovicesCreatePaymentWizard, self)._validate(invoices)
        # Same Payment Type
        types = list(set(invoices.mapped('payment_type')))
        if len(types) > 1:
            raise ValidationError(
                _('Please select invoice(s) with same payment type!'))
        return res

    @api.multi
    def action_create_payment(self):
        res = super(InovicesCreatePaymentWizard, self).action_create_payment()
        invoice_ids = self._context.get('active_ids', [])
        invoices = self.env['account.invoice'].browse(invoice_ids)
        res['context'].update({
            'default_payment_type': invoices[0].payment_type,
        })
        return res
