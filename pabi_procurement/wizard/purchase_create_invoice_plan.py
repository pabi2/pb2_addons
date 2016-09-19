# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.tools.float_utils import float_round as round


class PurchaseCreateInvoicePlan(models.TransientModel):
    _inherit = 'purchase.create.invoice.plan'

    @api.model
    def _prepare_installment_line(self, order, order_line, install):
        res = super(PurchaseCreateInvoicePlan, self).\
            _prepare_installment_line(order, order_line, install)
        return res
