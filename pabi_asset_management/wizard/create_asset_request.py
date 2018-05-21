# -*- coding: utf-8 -*-
from openerp import models, fields, api


class CreateAssetRequest(models.TransientModel):
    _name = 'create.asset.request'

    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        required=True,
    )
    building_id = fields.Many2one(
        'res.building',
        string='Building',
        ondelete='restrict',
    )
    floor_id = fields.Many2one(
        'res.floor',
        string='Floor',
        ondelete='restrict',
    )
    room_id = fields.Many2one(
        'res.room',
        string='Room',
        ondelete='restrict',
    )

    # Building / Floor / Room
    @api.multi
    @api.constrains('building_id', 'floor_id', 'room_id')
    def _check_building(self):
        for rec in self:
            self.env['res.building']._check_room_location(rec.building_id,
                                                          rec.floor_id,
                                                          rec.room_id)

    @api.onchange('building_id')
    def _onchange_building_id(self):
        self.floor_id = False
        self.room_id = False

    @api.onchange('floor_id')
    def _onchange_floor_id(self):
        self.room_id = False

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
            'default_building_id': self.building_id.id,
            'default_floor_id': self.floor_id.id,
            'default_room_id': self.room_id.id,
            'default_responsible_user_id': self.responsible_user_id.id,
        }
        result.update({'views': False,
                       'view_id': False,
                       'view_mode': 'form',
                       'context': ctx})
        return result
