# -*- coding: utf-8 -*-
from openerp import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        self.ensure_one()
        res = super(StockPicking, self).do_transfer()
        installment = self._context.get('installment', False)
        if not installment:
            return res
        # case invoice plan
        stock_move_obj = self.env['stock.move']
        invoice_obj = self.env['account.invoice']
        stock_move_ids = stock_move_obj.search([('picking_id', '=', self.ids)])
        inv_ids = invoice_obj.search([('source_document', '=', self.origin)])
        invoice_id = inv_ids.filtered(lambda l: l.installment == installment)
        for move_id in stock_move_ids:
            inv_line = invoice_id.invoice_line.filtered(
                lambda l: l.purchase_line_id == move_id.purchase_line_id)
            if not inv_line.move_id:
                inv_line.write({'move_id': move_id.id})
        return res
