# -*- coding: utf-8 -*-
# © 2015 TrinityRoots
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class PurchaseRequestLineMakePurchaseRequisition(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition"

    @api.model
    def _prepare_purchase_requisition_line(self, pr, item):
        res = super(PurchaseRequestLineMakePurchaseRequisition, self)\
            ._prepare_purchase_requisition_line(pr, item)
        if 'price_unit' not in res:
            res.update({'price_unit': item.product_price})
        return res

    @api.model
    def _prepare_item(self, line):
        res = super(PurchaseRequestLineMakePurchaseRequisition, self)\
            ._prepare_item(line)
        if 'product_price' not in res:
            res.update({'product_price': line.product_price})
        return res


class PurchaseRequestLineMakePurchaseRequisitionItem(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition.item"

    product_price = fields.Float(
        'Unit Price',
        track_visibility='onchange',
    )
