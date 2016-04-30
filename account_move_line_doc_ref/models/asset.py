# -*- coding: utf-8 -*-
from openerp import models, api


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    @api.multi
    def create_move(self):
        move_ids = super(AccountAssetDepreciationLine, self).create_move()
        moves = self.env['account.move'].browse(move_ids)
        for move in moves:
            if move.line_id:
                asset_name = self.env['account.move.line'].search(
                    [('id', 'in', move.line_id.ids),
                     ('asset_id', '!=', False)], limit=1).asset_id.name
                move.line_id.write({'doc_ref': asset_name or False})
        return move_ids
