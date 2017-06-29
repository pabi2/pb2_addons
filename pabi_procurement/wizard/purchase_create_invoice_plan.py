# -*- coding: utf-8 -*-
from openerp import models, api


class PurchaseCreateInvoicePlan(models.TransientModel):
    _inherit = 'purchase.create.invoice.plan'

    @api.model
    def _prepare_installment_line(self, order, order_line, install):
        res = super(PurchaseCreateInvoicePlan, self).\
            _prepare_installment_line(order, order_line, install)
        if install.description:
            res.update({
                'description': install.description,
            })
        return res
