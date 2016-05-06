# -*- coding: utf-8 -*-
from openerp import fields, models


class PurchaseRequestLineMakePurchaseRequisition(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition"

    operating_unit_id = fields.Many2one(required=True)
