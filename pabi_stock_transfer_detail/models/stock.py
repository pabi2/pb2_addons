# -*- coding: utf-8 -*-

from openerp import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_enter_transfer_details(self):
        self.ensure_one()
        context = self._context.copy()
        acceptance_id = self.acceptance_id.id
        context.update({'acceptance': acceptance_id})
        self = self.with_context(context)
        return super(StockPicking, self).do_enter_transfer_details()
