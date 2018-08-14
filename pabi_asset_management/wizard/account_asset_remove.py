# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


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
        readonly=True,
        default=lambda self: self._default_journal()
    )

    @api.model
    def _default_journal(self):
        journal = self.env['account.journal'].search([
            ('asset', '=', True), ('analytic_journal_id', '=', False)])
        if len(journal) != 1:
            raise ValidationError(_('No valid Asset Journal (No-Budget)'))
        return journal

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
