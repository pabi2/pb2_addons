# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    asset_adjust_id = fields.Many2one(
        'account.asset.adjust',
        string='Asset Adjustment',
        readonly=True,
        copy=False,
    )

    @api.multi
    def action_open_asset_adjust(self):
        self.ensure_one()
        action = self.env.ref('pabi_asset_management.'
                              'action_account_asset_adjust')
        if not action:
            raise ValidationError(_('No Action'))
        res = action.read([])[0]
        res['domain'] = [('id', '=', self.asset_adjust_id.id)]
        return res


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
