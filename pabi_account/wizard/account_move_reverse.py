# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountMoveReverse(models.TransientModel):
    _inherit = 'account.move.reverse'

    move_prefix = fields.Char(
        default=lambda self: self._default_move_prefix(),
    )

    @api.model
    def _default_move_prefix(self):
        move_ids = self._context.get('active_ids', False)
        if move_ids and len(move_ids) == 1:
            move = self.env['account.move'].browse(move_ids[0])
            return '%s - ' % move.name
