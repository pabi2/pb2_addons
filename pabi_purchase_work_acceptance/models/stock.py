# -*- coding: utf-8 -*-

from openerp import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    acceptance_id = fields.Many2one(
        'purchase.work.acceptance',
        string='Work Acceptance',
        domain="[('state', 'not in', ('done','cancel')),"
               "('order_id', '=', origin)]",
    )

    @api.model
    def _create_invoice_from_picking(self, picking, vals):
        acceptance = picking.acceptance_id
        if acceptance:
            vals.update({
                'origin': "%s:%s" % (
                    vals['origin'],
                    acceptance.name,
                ),
                'date_invoice': acceptance.date_invoice,
                'supplier_invoice_number': acceptance.supplier_invoice,
                'reference': acceptance.order_id.name,
            })
        res = super(StockPicking,
                    self)._create_invoice_from_picking(picking, vals)
        return res
