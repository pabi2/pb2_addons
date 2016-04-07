# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseCreateInvoice(models.TransientModel):
    _name = 'purchase.create.invoice'
    _description = 'Create Purchase Invoice'

    create_invoice = fields.Boolean('Create Invoices?')

    @api.multi
    def create_purchase_invoices(self):
        invoice_ids = []
        for record in self:
            if record.create_invoice:
                order_ids = self.env.context.get('active_ids')
                purchase_orders = self.env['purchase.order'].browse(order_ids)
                for order in purchase_orders:
                    if not order.invoice_ids:
                        inv_ids = order.action_invoice_create()
                        invoice_ids.append(inv_ids)
                    else:
                        for invoice in order.invoice_ids:
                            if not invoice.copy_invoice_id and \
                                invoice.state == 'cancel':
                                new_invoice = invoice.copy()
                                order.invoice_ids += new_invoice
                                invoice.copy_invoice_id = new_invoice
        return True
