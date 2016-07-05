# -*- coding: utf-8 -*-

from openerp import fields, models, api
import openerp.addons.decimal_precision as dp


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    confirmed_by = fields.Many2one(
        'res.users',
        string='Confirmed By',
        readonly=True,
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
    )
    verified = fields.Boolean(
        string='Verified',
        readonly=True,
        copy=False,
    )
    description = fields.Text(
        string='Internal Note',
    )

    _defaults = {
        'move_type': 'one',
    }

    @api.multi
    def action_verify(self):
        assert len(self) == 1, \
            'This action should only be used for a single id at a time.'
        self.verified = True
        return True

    @api.multi
    def action_reject(self):
        assert len(self) == 1, \
            'This action should only be used for a single id at a time.'
        res = super(StockPicking, self).do_unreserve()
        return res

    @api.multi
    def action_confirm(self):
        assert len(self) == 1, \
            'This action should only be used for a single id at a time.'
        res = super(StockPicking, self).action_confirm()
        if self.picking_type_code != 'internal':
            self.verified = True
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    request_qty = fields.Float(
        string='Request Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        required=True,
        default=0.0,
    )

    @api.onchange('request_qty')
    def _onchange_request_qty(self):
        self.product_uom_qty = self.request_qty
