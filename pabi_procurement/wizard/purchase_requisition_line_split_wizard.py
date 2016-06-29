# -*- coding: utf-8 -*-
from openerp import api, models
import itertools


class PurchaseRequisitionLineSplitWizard(models.TransientModel):
    _inherit = "purchase.requisition.line.split.wizard"

    @api.multi
    def split_requisition_line(self):
        self.ensure_one()
        for line in self.requisition_line_ids:
            # If number_split > 1
            if line.number_split > 1:
                for _ in itertools.repeat(None, line.number_split-1):
                    new_line = line.requisition_line_id.copy()
                    request_lines = line.requisition_line_id.\
                        purchase_request_lines.ids[0]
                    new_line.write({
                        'purchase_request_lines': [(4, request_lines)],
                    })
        return True
