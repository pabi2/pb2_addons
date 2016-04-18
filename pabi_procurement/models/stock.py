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
    state2 = fields.Selection(
        [
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('waiting', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('partially_available', 'Partially Available'),
            ('to_verify', 'To Verify'),
            ('assigned', 'Ready to Transfer'),
            ('done', 'Transferred'),
        ],
        string='Status',
        readonly=True,
        help="A dummy state used for Stock Picking",
    )

    _defaults = {
        'move_type': 'one',
        'state2': 'draft',
    }

    @api.multi
    def action_assign(self):
        res = super(StockPicking, self).action_assign()
        assert len(self) == 1, \
            'This action should only be used for a single id at a time.'
        if self.state == 'assigned':
            self.state2 = 'to_verify'
        return res

    @api.multi
    def action_verify(self):
        res = super(StockPicking, self).action_assign()
        assert len(self) == 1, \
            'This action should only be used for a single id at a time.'
        if self.state2 == 'to_verify':
            self.state2 = 'done'
        return res

    @api.multi
    def action_reject(self):
        res = super(StockPicking, self).action_assign()
        assert len(self) == 1, \
            'This action should only be used for a single id at a time.'
        if self.state2 == 'to_verify':
            self.state2 = 'draft'
            res = super(StockPicking, self).do_unreserve()
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
