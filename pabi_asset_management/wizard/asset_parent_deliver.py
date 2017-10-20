# -*- coding: utf-8 -*-
import datetime
from openerp import api, models, fields


class AssetParentDeliver(models.TransientModel):
    _name = 'asset.parent.deliver'
    _description = 'This wizard will mark all child asset as delivered'

    deliver_to = fields.Char(
        string='Deliver to',
        required=True,
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
        status_deliver = self.env.ref('pabi_asset_management.'
                                      'asset_status_deliver')
        parent_asset.child_ids.write({'status': status_deliver.id,
                                      'deliver_to': self.deliver_to,
                                      'deliver_date': self.deliver_date})
        parent_asset.state = 'delivered'
        return True
