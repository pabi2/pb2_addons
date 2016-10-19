# -*- coding: utf-8 -*-
from openerp import models, api


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    @api.multi
    def create_approval_no(self):
        super(PurchaseRequisition, self).create_approval_no()
        doctype = self.env['res.doctype'].search([('refer_type', '=',
                                                   'approval_report')])
        for rec in self:
            sequence_id = doctype.sequence_id.id
            fiscalyear_id = self.env['account.fiscalyear'].find()
            next_number = self.with_context(fiscalyear_id=fiscalyear_id).\
                env['ir.sequence'].next_by_id(sequence_id)
            rec.doc_no = next_number
