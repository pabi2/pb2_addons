# -*- coding: utf-8 -*-
from openerp import models, fields


class PurchaseRequestLineMakePurchaseRequisitionItem(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition.item"

    activity_rpt_id = fields.Many2one(
        'account.activity',
        string='Activity',
        required=False,
    )
