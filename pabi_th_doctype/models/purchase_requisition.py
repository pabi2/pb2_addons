# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    name = fields.Char(
        default=False,  # Overwrite, make sure no number is created
    )

    @api.model
    def create(self, vals):
        # Find doctype_id
        refer_type = 'purchase_requisition'
        doctype = self.env['res.doctype'].get_doctype(refer_type)
        fiscalyear_id = self.env['account.fiscalyear'].find()
        # --
        self = self.with_context(doctype_id=doctype.id,
                                 fiscalyear_id=fiscalyear_id)
        # It will try to use doctype_id first, if not available, rollback
        name = self.env['ir.sequence'].get('purchase.order.requisition')
        vals.update({'name': name})
        return super(PurchaseRequisition, self).create(vals)

    @api.multi
    def create_approval_no(self):
        refer_type = 'approval_report'
        doctype = self.env['res.doctype'].get_doctype(refer_type)
        fiscalyear_id = self.env['account.fiscalyear'].find()
        # --
        self = self.with_context(doctype_id=doctype.id,
                                 fiscalyear_id=fiscalyear_id)
        super(PurchaseRequisition, self).create_approval_no()
        return True
