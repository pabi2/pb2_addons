# -*- coding: utf-8 -*-
from datetime import datetime
from openerp import models, fields, api


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    @api.model
    def _get_extend_columns_for_fast_create(self, group_uuid):
        """ More fields value for record creation """
        now = fields.Datetime.context_timestamp(self, datetime.now())
        today = fields.Date.context_today(self)
        company_id = self.env.user.company_id.id
        user_id = self.env.user.id
        ou_id = self.env.user.default_operating_unit_id.id
        system_id = self.env.ref('pabi_interface.system_pabi2').id
        return {  # more default value to create the record
            'account_move': {
                'create_uid': user_id,
                'create_date': now,
                'write_uid': user_id,
                'write_date': now,
                'company_id': company_id,
                'state': 'draft',
                'to_check': False,
                'to_be_reversed': False,
                'cancel_entry': False,
                'system_id': system_id,
                'doctype': 'adjustment',
                'date_value': 'value.date',  # Special value
                'date_document': today,
                'narration': group_uuid,
            },
            'account_move_line': {
                'charge_type': 'external',
                'create_uid': user_id,
                'create_date': now,
                'write_uid': user_id,
                'write_date': now,
                'company_id': company_id,
                'blocked': False,
                'centralisation': 'normal',
                'date_created': today,
                'operating_unit_id': ou_id,
                'doctype': 'adjustment',
                'date_value': 'value.date',
                'is_tax_line': False,
            }
        }


class AccountAssetLine(models.Model):
    _inherit = 'account.asset.line'

    @api.multi
    def _setup_move_data(self, depreciation_date, period):
        self.ensure_one()
        move_data = super(AccountAssetLine, self).\
            _setup_move_data(depreciation_date, period)
        move_data['asset_depre_batch_id'] = self._context.get('batch_id',
                                                              False)
        return move_data

    @api.multi
    def _setup_move_line_data(self, depreciation_date,
                              period, account, type, move_id):
        move_line_data = super(AccountAssetLine, self).\
            _setup_move_line_data(depreciation_date,
                                  period, account, type, move_id)
        move_line_data['asset_depre_batch_id'] = self._context.get('batch_id',
                                                                   False)
        return move_line_data
