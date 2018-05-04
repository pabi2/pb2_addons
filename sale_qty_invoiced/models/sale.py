# -*- coding: utf-8 -*-

from openerp import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

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

    @api.depends('invoice_lines.invoice_id.state')
    def _compute_open_invoiced_qty(self):
        Uom = self.env['product.uom']
        for so_line in self:
            open_invoiced_qty = 0.0
            for invoice_line in so_line.invoice_lines:
                invoice = invoice_line.invoice_id
                if invoice.state and invoice.state not in ['draft', 'cancel']:
                    # Invoiced Qty in SO Line's UOM
                    open_invoiced_qty += \
                        Uom._compute_qty(invoice_line.uos_id.id,
                                         invoice_line.quantity,
                                         so_line.product_uom.id)
            so_line.open_invoiced_qty = min(so_line.product_uos_qty,
                                            open_invoiced_qty)
