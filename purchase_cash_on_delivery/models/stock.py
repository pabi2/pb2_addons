# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_done(self):
        # Find all POs of all sock move lines, so we can check only once
        purchase_ids = [move.purchase_line_id.order_id.id for move in self]
        purchase_ids = list(set(purchase_ids))
        if False in purchase_ids:
            purchase_ids.remove(False)
        purchases = self.env['purchase.order'].browse(purchase_ids)
        # Validate COD
        purchases._validate_purchase_cod_fully_paid()
        # --
        return super(StockMove, self).action_done()


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        # Remove any analytic lines in case of COD
        for picking in self:
            # Check whether this is prepaid
            prepaid = picking.move_lines.\
                mapped('purchase_line_id.order_id.is_prepaid')
            if len(prepaid) > 1:
                raise ValidationError(_('Mixing COD and non-COD not allowed.'))
            # If COD, delete analytic lines previously created by account move.
            elif prepaid and prepaid[0]:
                moves = self.env['account.move'].search(
                    [('document', '=', picking.name)])
                for move in moves:
                    move.line_id.mapped('analytic_lines').unlink()
        return res
