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

    @api.multi
    def _budget_eligible_move_lines(self):
        move_lines = super(AccountMoveLine, self)._budget_eligible_move_lines()
        # Add move line with fixed asset account
        move_lines += self.filtered(
            lambda l: l.account_id.user_type.for_asset and
            (l.activity_id or l.product_id)  # Is Activity or Product
        )
        return move_lines
