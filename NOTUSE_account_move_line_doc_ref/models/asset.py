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
                asset = self.env['account.move.line'].search(
                    [('id', 'in', move.line_id.ids),
                     ('asset_id', '!=', False)], limit=1).asset_id
                move.line_id.write(
                    {'doc_ref': asset.name or False,
                     'doc_id': '%s,%s' % ('account.asset.asset', asset.id)})
        return move_ids
