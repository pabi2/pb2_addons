# -*- coding: utf-8 -*-

from openerp import fields, models


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    cancel_reason_txt = fields.Char(
        string="Description",
        readonly=True,
        size=500,
    )
