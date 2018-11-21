# -*- coding: utf-8 -*-
from openerp import models, fields, api


class GenerateAssetCode(models.TransientModel):
    _name = 'generate.asset.code'

    filter_by = fields.Selection(
        [('null_asset_code', 'Asset Code is Null')],
        string='Filter By',
        default='null_asset_code',
        required=True,
    )

    @api.multi
    def action_apply(self):
        self.ensure_one()
        context = self._context.copy()
        active_model = context.get('active_model', False)
        active_ids = context.get('active_ids', [])
        if active_model and active_ids:
            invest_asset = self.env[active_model].browse(active_ids)
            if self.filter_by == 'null_asset_code':
                invest_asset = invest_asset.filtered(lambda l: not l.code)
            invest_asset.generate_code()
