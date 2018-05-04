# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseCreateInvoice(models.TransientModel):
    _inherit = 'purchase.create.invoice'

    async_process = fields.Boolean(
        string='Run task in background?',
        default=False,
    )

    @api.multi
    def create_purchase_invoices(self):
        self = self.with_context(async_process=self.async_process)
        return super(PurchaseCreateInvoice, self).create_purchase_invoices()
