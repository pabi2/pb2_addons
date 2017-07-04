# -*- coding: utf-8 -*-
from openerp import models, fields, api


class CreateAssetRequest(models.TransientModel):
    _name = 'create.asset.request'

    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        required=True,
    )
    location_id = fields.Many2one(
        'account.asset.location',
        string='Building',
    )
    room = fields.Char(
        string='Room',
    )

    @api.model
    def default_get(self, field_list):
        active_model = self._context.get('active_model')
        asset_ids = self._context.get('active_ids')
        assets = self.env[active_model].browse(asset_ids)
        assets.validate_asset_to_request()
        res = super(CreateAssetRequest, self).default_get(field_list)
        return res

    @api.multi
    def action_create_asset_request(self):
        self.ensure_one()
        asset_ids = self._context.get('active_ids', [])
        action = self.env.ref('pabi_asset_management.'
                              'action_account_asset_request')
        result = action.read()[0]
        ctx = {
            'selected_asset_ids': asset_ids,
            'default_location_id': self.location_id.id,
            'default_room': self.room,
            'default_responsible_user_id': self.responsible_user_id.id,
        }
        result.update({'views': False,
                       'view_id': False,
                       'view_mode': 'form',
                       'context': ctx})
        return result
