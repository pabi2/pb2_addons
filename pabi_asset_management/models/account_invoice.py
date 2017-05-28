# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.constrains('asset_category_id', 'asset_id')
    def _check_asset_id(self):
        for rec in self:
            if rec.asset_category_id or rec.asset_id:
                raise ValidationError(
                    _('For PABI2, creating asset on invoice is not allowed.'))
