# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def generate_purchase_invoice_plan(
            self, purchase_id, installment_date, num_installment=1,
            installment_amount=False, interval=1, interval_type='month',
            invoice_mode='change_price', use_advance=False,
            use_deposit=False, use_retention=False):

        self = self.with_context(active_model=self._name,
                                 active_id=purchase_id)
        # Mock wizard
        Wizard = self.env['purchase.create.invoice.plan']
        res = Wizard.default_get([])
        print res
        res['installment_date'] = installment_date
        res['num_installment'] = num_installment
        res['num_installment'] = installment_amount
        res['interval'] = interval
        res['interval_type'] = interval_type
        res['invoice_mode'] = invoice_mode
        res['use_advance'] = use_advance
        res['use_deposit'] = use_deposit
        res['use_retention'] = use_retention
        wizard = Wizard.create(res)
        wizard._onchange_plan()
        # Now, installment is crated as <newID> we need to make it persistant
        installments = []
        for line in wizard.installment_ids:
            installments.append((0, 0, line._convert_to_write(line._cache)))
        wizard.write({'installment_ids': installments})
        print wizard.installment_ids
        x = 1/0
        wizard.do_create_purchase_invoice_plan()
        # print wizard.installment_amount
        return True
