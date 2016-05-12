# -*- coding: utf-8 -*-

from openerp import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    acceptance_id = fields.Many2one(
        'purchase.work.acceptance',
        string='Work Acceptance',
    )

    @api.model
    def _create_invoice_from_picking(self, picking, vals):
        if picking.acceptance_id:
            vals.update({
                'origin': "%s:%s" % (vals['origin'],
                                     picking.acceptance_id.name)
            })
        res = super(StockPicking,
                    self)._create_invoice_from_picking(picking, vals)
        return res
