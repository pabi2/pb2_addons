# -*- coding: utf-8 -*-
# © 2015 TrinityRoots
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class PurchaseRequestLineMakePurchaseRequisition(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition"

    @api.model
    def _get_requisition_line_search_domain(self, requisition, item):
        res = super(
            PurchaseRequestLineMakePurchaseRequisition, self
        )._get_requisition_line_search_domain(requisition, item)
        res.append(('product_name', '=', item.name))
        return res

    @api.model
    def _prepare_purchase_requisition_line(self, pr, item):
        res = super(
            PurchaseRequestLineMakePurchaseRequisition,
            self)._prepare_purchase_requisition_line(pr, item)
        if 'product_name' not in res:
            res['product_name'] = item.name
        return res
