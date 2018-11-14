# -*- coding: utf-8 -*-

from openerp import fields, models, api


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    cancel_reason_txt = fields.Char(
        string="Description",
        readonly=True,
        size=500,
    )

    @api.model
    def recompute_request_line_state(self):
        for req_line in self.line_ids:
            for request_lines in req_line.purchase_request_lines:
                [request_line._get_requisition_state() for request_line in
                 request_lines]
        return True
