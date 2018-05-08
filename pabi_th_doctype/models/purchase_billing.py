# -*- coding: utf-8 -*-
from openerp import models, api


class PurchaseBilling(models.Model):
    _inherit = 'purchase.billing'

    @api.multi
    def validate_billing(self):
        refer_type = 'purchase_billing'
        for billing in self:
            doctype = self.env['res.doctype'].get_doctype(refer_type)
            fiscalyear_id = self.env['account.fiscalyear'].find(billing.date)
            billing = billing.with_context(doctype_id=doctype.id,
                                           fiscalyear_id=fiscalyear_id)
            super(PurchaseBilling, billing).validate_billing()
        return True
