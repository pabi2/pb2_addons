# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseWorkAcceptance(models.Model):
    _inherit = 'purchase.work.acceptance'

    name = fields.Char(
        default=False,  # Overwrite, make sure no number is created
    )

    @api.model
    def create(self, vals):
        # Find doctype_id
        refer_type = 'work_acceptance'
        doctype = self.env['res.doctype'].get_doctype(refer_type)
        fiscalyear_id = self.env['account.fiscalyear'].find()
        # --
        self = self.with_context(doctype_id=doctype.id,
                                 fiscalyear_id=fiscalyear_id)
        # It will try to use doctype_id first, if not available, rollback
        name = self.env['ir.sequence'].get('purchase.work.acceptance')
        vals.update({'name': name})
        return super(PurchaseWorkAcceptance, self).create(vals)
