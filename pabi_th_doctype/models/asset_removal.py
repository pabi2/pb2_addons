# -*- coding: utf-8 -*-
from openerp import models, api


class AccountAssetRemoval(models.Model):
    _inherit = 'account.asset.removal'

    @api.model
    def create(self, vals):
        # Find doctype_id
        refer_type = 'asset_removal'
        doctype = self.env['res.doctype'].get_doctype(refer_type)
        fiscalyear_id = self.env['account.fiscalyear'].find()
        # --
        self = self.with_context(doctype_id=doctype.id,
                                 fiscalyear_id=fiscalyear_id)
        # It will try to use doctype_id first, if not available, rollback
        name = self.env['ir.sequence'].get('account.asset.removal')
        vals.update({'name': name})
        return super(AccountAssetRemoval, self).create(vals)
