# -*- coding: utf-8 -*-
from openerp import models, api


class LoanCustomerAgreement(models.Model):
    _inherit = 'loan.customer.agreement'

    @api.multi
    def mork_action_sign(self):
        self.action_sign()
        return True

    @api.multi
    def mork_create_installment_order(self):
        self.ensure_one()
        self = self.with_context(active_model=self._name, active_id=self.id,
                                 active_ids=[self.id])

        # Mork Wizard
        Wizard = self.env['loan.create.installment.order.wizard']
        res = Wizard.default_get(['install_amount', 'amount', 'date_order'])
        wizard = Wizard.create(res)

        # Create installment order
        self.create_installment_order(wizard.date_order)
        return True
