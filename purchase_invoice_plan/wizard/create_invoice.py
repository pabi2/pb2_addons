# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseCreateInvoice(models.TransientModel):
    _name = 'purchase.create.invoice'
    _description = 'Create Purchase Invoice'

    create_invoice = fields.Boolean('Create Invoices?')

    @api.multi
    def create_purchase_invoices(self):
        order_ids = self.env.context.get('active_ids')
        purchase_orders = self.env['purchase.order'].browse(order_ids)
        for record in self:
            if record.create_invoice:
                [order.action_invoice_create() for order in purchase_orders]
        return True
