# -*- coding: utf-8 -*-
from openerp import models, fields, api


class CreateAssetRemoval(models.TransientModel):
    _name = 'create.asset.removal'

    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        readonly=True,
        required=True,
        default=lambda self: self.env.user,
    )
    date_remove = fields.Date(
        string='Removal Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    target_status = fields.Selection(
        [('dispose', u'จำหน่าย'),
         ('lost', u'สูญหาย'), ],
        string='Target Status',
        required=True,
    )

    @api.model
    def default_get(self, field_list):
        active_model = self._context.get('active_model')
        asset_ids = self._context.get('active_ids')
        assets = self.env[active_model].browse(asset_ids)
        assets.validate_asset_to_removal()
        res = super(CreateAssetRemoval, self).default_get(field_list)
        return res

    @api.multi
    def action_create_asset_removal(self):
        self.ensure_one()
        asset_ids = self._context.get('active_ids', [])
        action = self.env.ref('pabi_asset_management.'
                              'action_account_asset_removal')
        result = action.read()[0]
        ctx = {
            'selected_asset_ids': asset_ids,
            'default_user_id': self.user_id.id,
            'default_target_status': self.target_status,
            'default_date_remove': self.date_remove,
        }
        result.update({'views': False,
                       'view_id': False,
                       'view_mode': 'form',
                       'context': ctx})
        return result
