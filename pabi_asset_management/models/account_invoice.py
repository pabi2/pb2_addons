# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.constrains('asset_profile_id', 'asset_id')
    def _check_asset_id(self):
        for rec in self:
            if rec.asset_profile_id or rec.asset_id:
                raise ValidationError(
                    _('For PABI2, creating asset on invoice is not allowed.'))

    @api.multi
    def onchange_account_id(self, product_id, partner_id, inv_type,
                            fposition_id, account_id):
        """ For PABI2, never assigin asset profile in invoice """
        res = super(AccountInvoiceLine, self).onchange_account_id(
            product_id, partner_id, inv_type, fposition_id, account_id)
        if 'value' in res:
            res['value'].update({'asset_profile_id': False})
        return res
