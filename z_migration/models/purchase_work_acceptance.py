# -*- coding: utf-8 -*-
from openerp import models, api


class PurchaseWorkAcceptance(models.Model):

    _inherit = 'purchase.work.acceptance'

    @api.model
    def mork_write_to_receive_qty(self):
        po_id = self._context.get('active_id', False)
        AcceptanceLines = self.env['purchase.work.acceptance.line']
        for acceptance in self.search([('order_id', '=', po_id)]):
            acceptance_lines = \
                AcceptanceLines.search([('acceptance_id', '=', acceptance.id)])
            for acceptance_line in acceptance_lines:
                acceptance_line.write(
                    {'to_receive_qty': acceptance_line.balance_qty})
        return True
