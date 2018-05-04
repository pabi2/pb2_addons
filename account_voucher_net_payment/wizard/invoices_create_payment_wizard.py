# -*- coding: utf-8 -*-
from openerp import models, api


class InovicesCreatePaymentWizard(models.TransientModel):
    _inherit = 'invoices.create.payment.wizard'

    @api.multi
    def action_create_payment(self):
        res = super(InovicesCreatePaymentWizard, self).action_create_payment()
        res['context'].update({
            'allow_net_payment': self._context.get('allow_net_payment', False),
        })
        return res
