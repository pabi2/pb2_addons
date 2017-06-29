# -*- encoding: utf-8 -*-
from openerp import fields, models, api, _


class AccountAssetRemove(models.TransientModel):
    _inherit = 'account.asset.remove'

    target_status = fields.Many2one(
        'account.asset.status',
        string='Asset Status',
        domain="[('map_state', '=', 'removed')]",
        required=True,
    )

    @api.multi
    def remove(self):
        self.ensure_one()
        res = super(AccountAssetRemove, self).remove()
        active_id = self._context.get('active_id')
        asset = self.env['account.asset'].browse(active_id)
        asset.status = self.target_status
        return res
