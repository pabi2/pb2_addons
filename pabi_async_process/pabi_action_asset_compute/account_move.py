# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    asset_depre_batch_id = fields.Many2one(
        'pabi.asset.depre.batch',
        string='Asset Depreciation Batch ID',
        readonly=True,
        help="To group move line on same computation",
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    asset_depre_batch_id = fields.Many2one(
        'pabi.asset.depre.batch',
        string='Asset Depreciation Batch ID',
        related='move_id.asset_depre_batch_id',
        store=True,
        help="To group move line on same computation",
    )
