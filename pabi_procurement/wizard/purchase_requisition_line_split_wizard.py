# -*- coding: utf-8 -*-
from openerp import api, models, fields
import itertools


class PurchaseRequisitionLineSplitWizard(models.TransientModel):
    _inherit = "purchase.requisition.line.split.wizard"

    @api.multi
    def split_requisition_line(self):
        self.ensure_one()
        default = {}
        for line in self.requisition_line_ids:
            # If number_split > 1
            if line.number_split > 1:
                for _ in itertools.repeat(None, line.number_split-1):
                    new_line = line.requisition_line_id.copy()
                    print new_line
                    new_line.write({
                      'purchase_request_lines': [(4, line.requisition_line_id.purchase_request_lines.ids[0])],
                    })
        return True
