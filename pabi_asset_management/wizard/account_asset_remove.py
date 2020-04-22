# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountAssetRemove(models.TransientModel):
    _inherit = 'account.asset.remove'

    target_status = fields.Many2one(
        'account.asset.status',
        string='Asset Status',
        domain="[('map_state_removed', '=', 'removed')]",
        required=True,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        domain=[('asset', '=', True), ('analytic_journal_id', '=', False)],
        required=True,
        help="Asset Journal (No-Budget)",
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

    def _get_removal_data(self, asset, residual_value):
        res = super(AccountAssetRemove, self)._get_removal_data(
            asset, residual_value)
        chartfield_id = asset.owner_section_id or asset.owner_project_id or \
            asset.owner_invest_asset_id or \
            asset.owner_invest_construction_phase_id or False
        asset.account_analytic_id.write({
            'section_id': asset.owner_section_id.id or False,
            'project_id': asset.owner_project_id.id or False,
            'invest_asset_id': asset.owner_invest_asset_id.id or False,
            'invest_construction_phase_id':
                asset.owner_invest_construction_phase_id.id or False,
            'costcenter_id': chartfield_id.costcenter_id.id or False,
        })
        return res
