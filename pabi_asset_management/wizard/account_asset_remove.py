# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountAssetRemove(models.TransientModel):
    _inherit = 'account.asset.remove'

    target_status = fields.Many2one(
        'account.asset.status',
        string='Asset Status',
        domain="[('map_state', '=', 'removed')]",
        required=True,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Adjustment Journal',
        required=True,
        domain=[('asset', '=', True)],
    )

    @api.multi
    def remove(self):
        self.ensure_one()
        active_id = self._context.get('active_id')
        asset = self.env['account.asset'].browse(active_id)
        # If no_depreciation, no early_removal
        if asset.no_depreciation:
            self = self.with_context(early_removal=False)
        if self.journal_id:
            self = self.with_context(overwrite_journal_id=self.journal_id.id)
        self = self.with_context(overwrite_move_name='/')
        res = super(AccountAssetRemove, self).remove()
        asset.status = self.target_status
        return res
