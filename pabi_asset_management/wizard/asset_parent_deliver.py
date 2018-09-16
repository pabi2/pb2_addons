# -*- coding: utf-8 -*-
from openerp import api, models, fields, _
from openerp.exceptions import ValidationError


class AssetParentDeliver(models.TransientModel):
    _name = 'asset.parent.deliver'
    _description = 'This wizard will mark all child asset as delivered'

    deliver_to = fields.Char(
        string='Deliver to',
        required=True,
        size=500,
    )
    deliver_date = fields.Date(
        string='Delivery date',
        required=True,
    )

    @api.multi
    def update_assets(self):
        self.ensure_one()
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        parent_asset = self.env[active_model].browse(active_id)
        if not parent_asset.child_ids:
            raise ValidationError(_('No child assets!'))
        status_deliver = self.env.ref('pabi_asset_management.'
                                      'asset_status_deliver')
        parent_asset.child_ids.write({'status': status_deliver.id,
                                      'deliver_to': self.deliver_to,
                                      'deliver_date': self.deliver_date})
        parent_asset.state = 'close'
        return True
