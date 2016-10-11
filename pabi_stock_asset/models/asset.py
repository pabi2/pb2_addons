# -*- coding: utf-8 -*-

from openerp import models, fields, api


class StockMove(models.Model):

    _inherit = 'stock.move'

    parent_asset_id = fields.Many2one(
        'account.asset.asset',
        string='Parent Asset'
    )

    @api.multi
    def write(self, vals):
        result = super(StockMove, self).write(vals)
        return result
