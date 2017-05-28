# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    stock_move_id = fields.Many2one(
        'stock.move',
        string='Stock Move',
        readonly=True,
        help="When account is created by a stock move (anglo saxon).",
    )

    @api.model
    def create(self, vals):
        move_line = super(AccountMoveLine, self).create(vals)
        if move_line.asset_id:
            sequence = move_line.product_id.sequence_id
            if not sequence:
                raise ValidationError(_('No asset sequence setup!'))
            code = self.env['ir.sequence'].next_by_id(sequence.id)
            move_line.asset_id.write({'product_id': move_line.product_id.id,
                                      'move_id': move_line.stock_move_id.id,
                                      'code': code, })
        return move_line
