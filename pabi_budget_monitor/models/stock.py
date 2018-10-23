# -*- coding: utf-8 -*-
from openerp import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _picking_budget_check(self):
        for picking in self:
            # Check ount picking in
            if picking.picking_type_id.code == 'incoming':
                moves = self.env['account.move'].search(
                    [('document', '=', picking.name)], order='date ASC')
                moves._move_budget_check()
        return True

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        self._picking_budget_check()
        return res
