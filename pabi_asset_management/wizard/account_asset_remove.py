# -*- encoding: utf-8 -*-
from openerp import fields, models, api, _


class AccountAssetMove(models.TransientModel):
    _inherit = 'account.asset.remove'

    target_status = fields.Selection(
        [('dispose', u'จำหน่าย'),
         ('lost', u'สูญหาย'), ],
        string='Target Status',
        required=True,
    )

    @api.multi
    def remove(self):
        self.ensure_one()
        res = super(AccountAssetMove, self).remove()
        active_id = self._context.get('active_id')
        asset = self.env['account.asset.asset'].browse(active_id)
        asset.status = self.target_status
        return res
