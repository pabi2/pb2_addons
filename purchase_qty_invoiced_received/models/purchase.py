# -*- coding: utf-8 -*-

from openerp import fields, models, api


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    open_invoiced_qty = fields.Float(
        string='Invoiced Quantity',
        digits=(12, 6),
        compute='_compute_open_invoiced_qty',
        store=True,
        copy=False,
        default=0.0,
        help="This field calculate invoiced quantity at line level. "
        "Will be used to calculate committed budget",
    )
    received_qty = fields.Float(
        string='Received Quantity',
        digits=(12, 6),
        compute='_compute_received_qty',
        store=True,
        copy=False,
        default=0.0,
        help="This field calculate received quantity at line level. ",
    )

    @api.depends('invoice_lines.invoice_id.state')
    def _compute_open_invoiced_qty(self):
        Uom = self.env['product.uom']
        for po_line in self.sudo():
            open_invoiced_qty = 0.0
            for invoice_line in po_line.invoice_lines:
                invoice = invoice_line.invoice_id
                if invoice.state and invoice.state not in ['draft', 'cancel']:
                    # Invoiced Qty in PO Line's UOM
                    open_invoiced_qty += \
                        Uom._compute_qty(invoice_line.uos_id.id,
                                         invoice_line.quantity,
                                         po_line.product_uom.id)
            po_line.open_invoiced_qty = min(po_line.product_qty,
                                            open_invoiced_qty)

    @api.depends('order_id.state', 'move_ids.state')
    def _compute_received_qty(self):
        for line in self:
            if line.order_id.state not in ['approved', 'except_picking',
                                           'except_invoice', 'done']:
                line.received_qty = 0.0
                continue
            if line.product_id.type not in ['consu', 'product']:
                line.received_qty = line.product_qty
                continue
            total = 0.0
            for move in line.move_ids:
                if move.state == 'done':
                    total += move.product_uom_qty
            line.received_qty = total
