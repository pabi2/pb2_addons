# -*- coding: utf-8 -*-
from openerp import models, api


class PaymentExport(models.Model):
    _inherit = 'payment.export'

    @api.model
    def create(self, vals):
        # Find doctype_id
        refer_type = 'payment_export'
        doctype = self.env['res.doctype'].get_doctype(refer_type)
        fiscalyear_id = self.env['account.fiscalyear'].find()
        # --
        self = self.with_context(doctype_id=doctype.id,
                                 fiscalyear_id=fiscalyear_id)
        return super(PaymentExport, self).create(vals)
